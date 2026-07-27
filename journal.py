from flask import session, Blueprint, render_template, request, redirect, url_for, make_response
from datetime import datetime
from database import get_db_conn, create_table
import calendar
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
from functools import wraps

journal = Blueprint("journal", __name__)


def requires_verification(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("verified"):
            return redirect(url_for("journal.verify"))

        return func(*args, **kwargs)

    return wrapper


@journal.before_request
def check_table():
    create_table("""
    CREATE TABLE IF NOT EXISTS journal_days (
        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        date DATE UNIQUE NOT NULL,
        cipher_text TEXT NOT NULL,
        iv TEXT NOT NULL,
        character_count INTEGER,
        edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")


@requires_verification
def decrypt_entry(cipher_text, iv):
    key = session.get("encryption_key")

    if not key:
        raise Exception("No encryption key in session")

    # Convert stored values back into bytes
    ciphertext = base64.b64decode(cipher_text)
    nonce = base64.b64decode(iv)

    # Convert stored key back into bytes if stored as base64
    key = base64.b64decode(key)

    aes = AESGCM(key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode("utf-8")


@requires_verification
def encrypt_entry(content):
    key = session.get("encryption_key")

    if not key:
        raise Exception("No encryption key in session")

    # Convert stored base64 key back into bytes
    key = base64.b64decode(key)

    aes = AESGCM(key)

    # AES-GCM uses a 12-byte nonce (often called IV)
    iv = os.urandom(12)

    ciphertext = aes.encrypt(
        iv,
        content.encode("utf-8"),
        None
    )

    return (
        base64.b64encode(ciphertext).decode("utf-8"),
        base64.b64encode(iv).decode("utf-8")
    )


def format_journal_date(year, month, day, full=False):
    date = datetime(year, month, day)

    if 11 <= day % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    if full:
        return date.strftime(f"%A the {day}{suffix} of %B")
    else:
        return date.strftime(f"%A the {day}{suffix}")


@journal.route("/")
@requires_verification
def journal_index():

    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    now = datetime.now()

    today = None

    if month is None:
        month = now.month
    if year is None:
        year = now.year
    if month < 1 or month > 12:
        month = now.month

    if month == now.month and year == now.year:
        today = now.day

    days_in_month = calendar.monthrange(year, month)[1]

    days_dict = {}

    conn, cur = get_db_conn()

    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, days_in_month).date()

    query = """
        SELECT id, date, cipher_text, iv, character_count, edited_at
        FROM journal_days
        WHERE date BETWEEN %s AND %s
    """

    cur.execute(query, (start_date, end_date))

    rows = cur.fetchall()

    journal_entries = {
        row[1].day: {
            "id": row[0],
            "date": row[1],
            "content": decrypt_entry(row[2], row[3]),
            "character_count": row[4],
            "edited_at": row[5]
        }
        for row in rows
    }

    for day_i in range(1, days_in_month + 1):

        if day_i in journal_entries:
            days_dict[day_i] = {
                "name": format_journal_date(year, month, day_i),
                "data": (
                    journal_entries[day_i]["id"],
                    journal_entries[day_i]["content"],
                    journal_entries[day_i]["edited_at"]
                )
            }

        else:
            days_dict[day_i] = {
                "name": format_journal_date(year, month, day_i),
                "data": None
            }

    conn.close()

    response = render_template(
        "journal/index.html",
        title="Journal",
        days_dict=days_dict,
        today=today,
        month=month,
        year=year,
        days_in_month=days_in_month,
    )

    resp = make_response(response)
    resp.headers["Cache-Control"] = "no-store"

    return resp


@journal.route("/create/<int:y>/<int:m>/<int:d>")
@requires_verification
def create_log(y, m, d):

    conn, cur = get_db_conn()

    date_value = datetime(y, m, d).date()

    # Create an empty encrypted journal entry
    cipher_text, iv = encrypt_entry("")

    query = """
        INSERT INTO journal_days
        (date, cipher_text, iv, character_count)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING
        RETURNING id
    """

    cur.execute(
        query,
        (
            date_value,
            cipher_text,
            iv,
            0
        )
    )

    row = cur.fetchone()

    # Entry already existed
    if row is None:
        cur.execute(
            "SELECT id FROM journal_days WHERE date = %s",
            (date_value,)
        )
        log_id = cur.fetchone()[0]
    else:
        log_id = row[0]

    conn.commit()
    conn.close()

    return redirect(
        url_for("journal.edit_log", log_id=log_id)
    )


@journal.route("/edit/<int:log_id>")
@requires_verification
def edit_log(log_id):

    conn, cur = get_db_conn()

    query = """
        SELECT date, cipher_text, iv
        FROM journal_days
        WHERE id = %s
    """

    cur.execute(query, (log_id,))

    row = cur.fetchone()

    if row is None:
        conn.close()
        return redirect(
            url_for(
                "journal.create_log",
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
        )

    date = row[0]

    content = decrypt_entry(
        row[1],
        row[2]
    )

    date_formatted = format_journal_date(
        date.year,
        date.month,
        date.day,
        True
    )

    conn.close()

    return render_template(
        "journal/edit-log.html",
        title=f"Journal - {date_formatted}",
        log_id=log_id,
        date_formatted=date_formatted,
        content=content
    )


@journal.route("/edit-log-input/<int:log_id>", methods=["POST"])
@requires_verification
def edit_log_input(log_id):

    data = request.get_json()

    content = data["content"]

    cipher_text, iv = encrypt_entry(content)

    timestamp = datetime.now()

    conn, cur = get_db_conn()

    query = """
        UPDATE journal_days
        SET cipher_text = %s,
            iv = %s,
            character_count = %s,
            edited_at = %s
        WHERE id = %s
    """

    cur.execute(
        query,
        (
            cipher_text,
            iv,
            len(content),
            timestamp,
            log_id
        )
    )

    conn.commit()
    conn.close()

    return {"status": "saved"}


@journal.route("/verify")
def verify():
    return render_template("journal/verify.html")


@journal.route("/verify-input", methods=["POST"])
def verify_input():

    passkey = request.form.get("passkey")

    correct_passkey = os.environ.get("JOURNAL_PASSKEY")

    if passkey and passkey == correct_passkey:

        # Derive a 256-bit encryption key from the passkey
        encryption_key = hash_secret_raw(
            secret=passkey.encode("utf-8"),
            salt=b"journal-encryption-salt",
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            type=Type.ID
        )

        session["verified"] = True

        # Store as base64 because Flask sessions store text safely
        session["encryption_key"] = base64.b64encode(
            encryption_key
        ).decode("utf-8")

        return redirect(url_for("journal.journal_index"))

    return redirect(url_for("journal.verify"))


@journal.route("/logout")
def logout():

    session.pop("verified", None)
    session.pop("encryption_key", None)

    return redirect(url_for("journal.verify"))