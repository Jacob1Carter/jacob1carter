from flask import session, Blueprint, render_template, request, redirect, url_for, make_response
from datetime import datetime
from database import get_db_conn, create_table
import calendar

journal = Blueprint("journal", __name__)


@journal.before_request
def check_table():
    create_table("""
    CREATE TABLE IF NOT EXISTS journal_days (
    
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    content TEXT DEFAULT '',
    edited_at TEXT NOT NULL
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

    today = None

    if month is None:
        month = datetime.now().month
        today = datetime.now().day

    if year is None:
        year = datetime.now().year

    days_in_month = calendar.monthrange(year, month)[1]

    days_dict = {}

    conn, cur = get_db_conn()
    for day_i in range(1, days_in_month+1):
        date_str = f"{year:04d}-{month:02d}-{day_i:02d}"
        query = "SELECT id, content, edited_at FROM journal_days WHERE date = ?"
        cur.execute(query, (date_str,))
        row = cur.fetchone()
        if row:
            days_dict[day_i] = {
                "name": format_journal_date(year, month, day_i),
                "data": row
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
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    query = "SELECT id FROM  journal_days WHERE date = ?"
    cur.execute(query, (date_str,))
    log_id = cur.fetchone()
    if not log_id:
        query = "INSERT INTO journal_days (date, edited_at) VALUES (?, ?)"
        cur.execute(query, (date_str, datetime.now()))
        log_id = cur.lastrowid
        conn.commit()
    
    conn.close()
    return redirect(url_for("journal.edit_log", log_id=log_id))


@journal.route("/edit/<log_id>")
def edit_log(log_id):
    conn, cur = get_db_conn()
    query = "SELECT date, content FROM journal_days WHERE id = ?"
    cur.execute(query, (log_id,))
    row = cur.fetchone()
    date = row[0]
    content = row[1]
    year, month, day = date.split("-")
    date_formatted = format_journal_date(int(year), int(month), int(day), True)
    return render_template("journal/edit-log.html", title=f"Journal - {date_formatted}", log_id=log_id, date_formatted=date_formatted, content=content)


@journal.route("/edit-log-input/<int:log_id>", methods=["POST"])
def edit_log_input(log_id):

    data = request.get_json()

    content = data["content"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn, cur = get_db_conn()

    query = """
        UPDATE journal_days
        SET content = ?, edited_at = ?
        WHERE id = ?
    """

    cur.execute(query, (content, timestamp, log_id))

    conn.commit()
    conn.close()

    return {"status": "saved"}