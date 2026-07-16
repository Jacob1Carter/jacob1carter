from flask import session, Blueprint, render_template, request, redirect, url_for, make_response
from datetime import datetime
from database import get_db_conn, create_table
import calendar

journal = Blueprint("journal", __name__)


@journal.before_request
def check_table():
    create_table("""
    CREATE TABLE IF NOT EXISTS journal_days (
    
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    content TEXT DEFAULT '',
    edited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")


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
        SELECT id, date, content, edited_at
        FROM journal_days
        WHERE date BETWEEN %s AND %s
    """

    cur.execute(query, (start_date, end_date))

    rows = cur.fetchall()

    journal_entries = {
        row[1].day: row
        for row in rows
    }

    for day_i in range(1, days_in_month + 1):

        if day_i in journal_entries:
            days_dict[day_i] = {
                "name": format_journal_date(year, month, day_i),
                "data": (
                    journal_entries[day_i][0],
                    journal_entries[day_i][2],
                    journal_entries[day_i][3]
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


@journal.route("/create/<int:year>/<int:month>/<int:day>")
def create_log(year, month, day):

    conn, cur = get_db_conn()

    date_value = datetime(year, month, day).date()

    query = """
        INSERT INTO journal_days (date)
        VALUES (%s)
        ON CONFLICT (date) DO UPDATE
        SET date = EXCLUDED.date
        RETURNING id
    """

    cur.execute(query, (date_value,))

    log_id = cur.fetchone()[0]

    conn.commit()
    conn.close()

    return redirect(url_for("journal.edit_log", log_id=log_id))


@journal.route("/edit/<log_id>")
def edit_log(log_id):

    conn, cur = get_db_conn()

    query = "SELECT date, content FROM journal_days WHERE id = %s"
    cur.execute(query, (log_id,))

    row = cur.fetchone()

    date = row[0]
    content = row[1]

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
def edit_log_input(log_id):

    data = request.get_json()

    content = data["content"]

    timestamp = datetime.now()

    conn, cur = get_db_conn()

    query = """
        UPDATE journal_days
        SET content = %s, edited_at = %s
        WHERE id = %s
    """

    cur.execute(query, (content, timestamp, log_id))

    conn.commit()
    conn.close()

    return {"status": "saved"}