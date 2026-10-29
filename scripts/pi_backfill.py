"""Copy existing Supabase rows into the Raspberry Pi PostgreSQL database.

The production app now reads and writes through PostgREST on the Pi (see
backend/db.py). This script is a one-time/repeatable helper for moving the
legacy Supabase data into that database.

Environment:
  SUPABASE_DATABASE_URL  source Postgres connection string
  PI_DATABASE_URL        destination Postgres connection string

Usage:
    python scripts/pi_backfill.py
    python scripts/pi_backfill.py --full
"""

import os
import sys

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

CHUNK = 500

# (table, watermark column, conflict column, columns)
# users has no serial id, so it is copied in full; existing emails are skipped.
TABLES = [
    (
        "users",
        None,
        "email",
        [
            "email",
            "first_name",
            "last_name",
            "organization",
            "password_hash",
            "auth_token",
            "time_created",
            "time_expiry",
            "package",
        ],
    ),
    ("ports", "id", "id", ["id", "country", "locode", "port", "latitude", "longitude"]),
    ("nmea_data", "id", "id", ["id", "nmea", "timestamp"]),
    (
        "sensor_data",
        "id",
        "id",
        ["id", "device_id", "voltage", "temperature", "nmea", "timestamp"],
    ),
    (
        "ais_data_sat",
        "id",
        "id",
        ["id", "time_stamp", "ch1", "ch2", "rssi", "data_column", "mmsi"],
    ),
]


def connect(name):
    url = os.environ.get(name, "").strip()
    if not url:
        raise SystemExit(f"{name} is not set")
    return psycopg2.connect(url)


def conflict_clause(key):
    return f"ON CONFLICT ({key}) DO NOTHING"


def reset_sequence(cursor, table):
    cursor.execute(
        "SELECT setval(pg_get_serial_sequence(%s, 'id'), "
        "COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM " + table,
        (table,),
    )


def copy_table(source, destination, table, watermark, key, columns, full):
    where = ""
    params = ()
    if watermark and not full:
        with destination.cursor() as cursor:
            cursor.execute(f"SELECT MAX({watermark}) FROM {table}")
            last = cursor.fetchone()[0]
        if last is not None:
            where = f"WHERE {watermark} > %s"
            params = (last,)

    with source.cursor() as cursor:
        cursor.execute(
            f"SELECT {', '.join(columns)} FROM {table} {where} ORDER BY {watermark or key}",
            params,
        )
        rows = cursor.fetchall()

    if not rows:
        print(f"{table}: nothing new")
        return 0

    sql = (
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s "
        f"{conflict_clause(key)}"
    )
    with destination.cursor() as cursor:
        for start in range(0, len(rows), CHUNK):
            execute_values(cursor, sql, rows[start:start + CHUNK], page_size=CHUNK)
        if watermark:
            reset_sequence(cursor, table)
    destination.commit()
    print(f"{table}: copied {len(rows)} rows")
    return len(rows)


def main(full=False):
    missing = [
        name
        for name in ("SUPABASE_DATABASE_URL", "PI_DATABASE_URL")
        if not os.environ.get(name, "").strip()
    ]
    if missing:
        raise SystemExit(f"Missing environment variable(s): {', '.join(missing)}")

    source = connect("SUPABASE_DATABASE_URL")
    destination = connect("PI_DATABASE_URL")
    try:
        total = 0
        for table, watermark, key, columns in TABLES:
            total += copy_table(source, destination, table, watermark, key, columns, full)
        print(f"Done: {total} rows copied")
    finally:
        source.close()
        destination.close()


if __name__ == "__main__":
    main(full="--full" in sys.argv)
