import psycopg
import os
import re


def get_db_conn():
    conn = psycopg.connect(
        os.environ["DATABASE_URL"]
    )
    cur = conn.cursor()
    return conn, cur


def construct_db():

    conn, cur = get_db_conn()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS db_tables (

        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        table_name TEXT NOT NULL,
        table_desc TEXT,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cur.execute(
        """
        SELECT 1 FROM db_tables 
        WHERE table_name = %s
        """,
        ("db_tables",)
    )

    if cur.fetchone() is None:

        cur.execute(
            """
            INSERT INTO db_tables
            (table_name, table_desc)
            VALUES (%s, %s)
            """,
            (
                "db_tables",
                "A table for all other tables"
            )
        )

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
            "SELECT 1 FROM db_tables WHERE table_name = %s LIMIT 1",
            (table_name,),
        )
        already_exists = cur.fetchone() is not None

        if not already_exists:
            cur.execute(query)
            cur.execute(
                "INSERT INTO db_tables (table_name) VALUES (%s)",
                (table_name,),
            )
            conn.commit()

        return already_exists

    finally:
        conn.close()
