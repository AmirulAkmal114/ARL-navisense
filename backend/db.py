import os

from dotenv import load_dotenv

import psycopg2
import psycopg2.extras

load_dotenv()

DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL", "")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("SUPABASE_DATABASE_URL is not set")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def query(sql, params=None, fetch="all"):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            if fetch == "all":
                return cur.fetchall()
            if fetch == "one":
                return cur.fetchone()
            return cur.rowcount
    finally:
        conn.close()


def insert_many(sql, rows):
    if not rows:
        return 0
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
            return cur.rowcount
    finally:
        conn.close()
