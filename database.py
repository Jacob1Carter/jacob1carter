import sqlite3
import os
import re


def get_db_conn():
    conn = sqlite3.connect("data/database.db")
    cur = conn.cursor()
    return conn, cur


def construct_db():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists("data/database.db"):
        with open("data/database.db", "w"):
            pass
        conn, cur = get_db_conn()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS db_tables (
        
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_name TEXT NOT NULL,
        table_desc TEXT,
        created_at_utc TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        
        cur.execute("INSERT INTO db_tables (table_name, table_desc) VALUES ('tb_tables', 'A table for all other tables')")

        conn.commit()
        conn.close()


def create_table(query):
    match = re.compile(
        r"^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)",
        re.IGNORECASE,
    ).match(query)

    if not match:
        raise ValueError("Query is not a valid CREATE TABLE statement.")

    table_name = match.group(1)

    conn, cur = get_db_conn()
    try:
        cur.execute(
            "SELECT 1 FROM db_tables WHERE table_name = ? LIMIT 1",
            (table_name,),
        )
        already_exists = cur.fetchone() is not None

        if not already_exists:
            cur.execute(query)
            cur.execute(
                "INSERT INTO db_tables (table_name) VALUES (?)",
                (table_name,),
            )
            conn.commit()

        return already_exists

    finally:
        conn.close()


def drop_db():
    if os.path.exists("data/database.db"):
        os.remove("data/database.db")
