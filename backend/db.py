import os

from dotenv import load_dotenv

import psycopg2
import psycopg2.extras

load_dotenv()

# Primary cloud database (Supabase).
DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL", "")

# Optional mirror: PostgreSQL running on the Raspberry Pi, reached through a
# Cloudflare Tunnel (e.g. postgresql://navisense:pass@pi-db.example.com:5432/navisense).
PI_DATABASE_URL = os.environ.get("PI_DATABASE_URL", "")

# SQL verbs treated as writes (mirrored to the Pi DB when configured).
_WRITE_PREFIXES = ("INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE")


def get_connection(url):
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(url)
    conn.autocommit = True
    return conn


def _execute(sql, params, fetch, url):
    conn = get_connection(url)
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


def _is_write(sql):
    return sql.lstrip().upper().startswith(_WRITE_PREFIXES)


def query(sql, params=None, fetch="all", mirror=False):
    """Run a query on the primary DB.

    Write statements (fetch="none" INSERT/UPDATE/...) are mirrored to the Pi DB
    when PI_DATABASE_URL is set. Pi failures are logged but never raised, so a
    dead Pi can never take the cloud app down.
    """
    result = _execute(sql, params, fetch, DATABASE_URL)
    if PI_DATABASE_URL and (mirror or (fetch == "none" and _is_write(sql))):
        try:
            _execute(sql, params, fetch, PI_DATABASE_URL)
        except Exception as exc:
            print(f"PI DB mirror skipped: {exc}")
    return result


def _insert_many(sql, rows, url):
    conn = get_connection(url)
    try:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
            return cur.rowcount
    finally:
        conn.close()


def insert_many(sql, rows):
    """Bulk insert into the primary DB, mirrored to the Pi DB when configured."""
    if not rows:
        return 0
    count = _insert_many(sql, rows, DATABASE_URL)
    if PI_DATABASE_URL:
        try:
            _insert_many(sql, rows, PI_DATABASE_URL)
        except Exception as exc:
            print(f"PI DB mirror skipped: {exc}")
    return count


def pi_query(sql, params=None, fetch="all"):
    """Run a query directly against the Raspberry Pi DB (used by backfill scripts)."""
    if not PI_DATABASE_URL:
        raise RuntimeError("PI_DATABASE_URL is not set")
    return _execute(sql, params, fetch, PI_DATABASE_URL)


def pi_insert_many(sql, rows):
    """Bulk insert directly into the Raspberry Pi DB (used by backfill scripts)."""
    if not rows:
        return 0
    if not PI_DATABASE_URL:
        raise RuntimeError("PI_DATABASE_URL is not set")
    return _insert_many(sql, rows, PI_DATABASE_URL)
