"""Helper to ensure the test database exists."""

import asyncio
import sys

import psycopg

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def init_test_db():
    conn = psycopg.connect(
        "postgresql://careerpilot_user:careerpilot_secure_dev_pass123@localhost:5433/careerpilot",
        autocommit=True,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'careerpilot_test'")
        if not cur.fetchone():
            cur.execute("CREATE DATABASE careerpilot_test OWNER careerpilot_user")
            print("Created database careerpilot_test")
        else:
            print("Database careerpilot_test already exists")
    conn.close()


if __name__ == "__main__":
    init_test_db()
