"""Sync Supabase (primary) data into the Raspberry Pi PostgreSQL.

Incremental by default: only rows newer than the Pi's current watermark are
copied, so it is safe to re-run. Use --full to copy everything (expect
conflicts to be skipped).

Usage:
    python scripts/pi_backfill.py
    python scripts/pi_backfill.py --full
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from backend.db import PI_DATABASE_URL, query, pi_insert_many, pi_query

load_dotenv()

CHUNK = 500

# (table, watermark column, columns)
TABLES = [
    ("users", "email", ["email", "first_name", "last_name", "organization",
                         "password_hash", "auth_token", "time_created",
                         "time_expiry", "package"]),
    ("ports", "id", ["id", "country", "locode", "port", "latitude", "longitude"]),
    ("nmea_data", "id", ["id", "nmea", "timestamp"]),
    ("sensor_data", "id", ["id", "device_id", "voltage", "temperature", "nmea", "timestamp"]),
    ("ais_data_sat", "id", ["id", "time_stamp", "ch1", "ch2", "rssi", "data_column", "mmsi"]),
]


def main(full: bool = False) -> None:
    if not PI_DATABASE_URL:
        print("PI_DATABASE_URL is not set in .env — nothing to do.")
        return

    for table, key, cols in TABLES:
        where, params = "", ()
        if not full:
            row = pi_query(f"SELECT MAX({key}) AS mx FROM {table}", fetch="one")
            mx = row["mx"] if row else None
            if mx is not None:
                where, params = f"WHERE {key} > %s", (mx,)

        rows = query(
            f"SELECT {', '.join(cols)} FROM {table} {where} ORDER BY {key}",
            params,
        )
        if not rows:
            print(f"{table}: nothing new")
            continue

        conflict = f"ON CONFLICT ({key}) DO NOTHING" if key != "id" else ""
        placeholders = ", ".join(["%s"] * len(cols))
        insert_sql = (
            f"INSERT INTO {table} ({', '.join(cols)}) "
            f"VALUES ({placeholders}) {conflict}"
        )
        tuples = [tuple(r[c] for c in cols) for r in rows]

        total = 0
        for i in range(0, len(tuples), CHUNK):
            chunk = tuples[i:i + CHUNK]
            try:
                total += pi_insert_many(insert_sql, chunk)
            except Exception as exc:
                print(f"{table}: chunk {i // CHUNK} failed: {exc}")
        print(f"{table}: copied {total} rows ({len(tuples)} seen)")


if __name__ == "__main__":
    main(full="--full" in sys.argv)
