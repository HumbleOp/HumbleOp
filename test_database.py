# test_database.py

import os
import sqlite3
import sys

DB_PATH = "humbleop.db"
EXPECTED_TABLES = [
    "users",
    "posts",
    "comments",
    "votes",
    "flags",
    "likes",
    "badges",
    "follows"
]

def connect_db(path):
    if not os.path.exists(path):
        print(f"❌ Database file not found: {path}")
        sys.exit(1)
    return sqlite3.connect(path)

def table_exists(conn, table):
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,)
    )
    return cur.fetchone() is not None

def count_rows(conn, table):
    cur = conn.execute(f"SELECT COUNT(*) FROM {table};")
    return cur.fetchone()[0]

def main():
    conn = connect_db(DB_PATH)
    print(f"🔍 Inspecting database: {DB_PATH}\n")

    for tbl in EXPECTED_TABLES:
        if table_exists(conn, tbl):
            cnt = count_rows(conn, tbl)
            print(f"✅ Table `{tbl}` exists — {cnt} rows")
        else:
            print(f"❌ Table `{tbl}` is missing!")

    conn.close()

if __name__ == "__main__":
    main()
