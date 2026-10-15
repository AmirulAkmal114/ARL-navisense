import argparse
import csv
import os
import sys
from datetime import timezone

import psycopg2
from dateutil.parser import isoparse
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL", "")
DEFAULT_BATCH_SIZE = 500


def parse_ts(value):
    if not value or not str(value).strip():
        return None
    dt = isoparse(str(value).strip())
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def read_rows(path, has_header, expected_columns, ts_idx):
    rows = []
    skipped_no_nmea = 0
    skipped_bad_ts = 0

    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        if has_header:
            header = next(reader, None)
            if header is None:
                return rows, skipped_no_nmea, skipped_bad_ts
            normalized = [h.strip().lower() for h in header]
            if "nmea" not in normalized:
                print(f"Header missing 'nmea' column (found: {header})")
                sys.exit(1)
            nmea_idx = normalized.index("nmea")
            if ts_idx is not None:
                ts_idx = normalized.index("timestamp") if "timestamp" in normalized else None
        else:
            nmea_idx = 0
            if ts_idx is None:
                ts_idx = 1

        for line in reader:
            if not line:
                continue
            nmea = (line[nmea_idx] or "").strip() if nmea_idx < len(line) else ""
            if not nmea:
                skipped_no_nmea += 1
                continue

            raw_ts = line[ts_idx] if ts_idx is not None and ts_idx < len(line) else None
            ts = None
            if raw_ts and str(raw_ts).strip():
                try:
                    ts = parse_ts(raw_ts)
                except ValueError:
                    skipped_bad_ts += 1

            rows.append((nmea, ts))

    return rows, skipped_no_nmea, skipped_bad_ts


def main():
    parser = argparse.ArgumentParser(description="Import NMEA CSV rows into nmea_data")
    parser.add_argument("--file", required=True, help="Path to the CSV file")
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="CSV has no header row (columns: nmea,timestamp)",
    )
    parser.add_argument(
        "--columns",
        default="nmea,timestamp",
        help="Comma-separated expected header columns (default: nmea,timestamp)",
    )
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count and validate rows only; do not write to the database",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    if not DATABASE_URL:
        print("SUPABASE_DATABASE_URL is not set")
        sys.exit(1)

    expected_columns = [c.strip().lower() for c in args.columns.split(",")]
    if "nmea" not in expected_columns:
        print("Columns must include 'nmea'")
        sys.exit(1)
    ts_idx = expected_columns.index("timestamp") if "timestamp" in expected_columns else None

    rows, skipped_no_nmea, skipped_bad_ts = read_rows(
        args.file, has_header=not args.no_header, expected_columns=expected_columns, ts_idx=ts_idx
    )

    print(f"Rows read: {len(rows)}")
    print(f"Skipped (blank nmea): {skipped_no_nmea}")
    print(f"Skipped (bad timestamp): {skipped_bad_ts}")

    if rows:
        first_ts = next((r[1] for r in rows if r[1]), None)
        last_ts = next((r[1] for r in reversed(rows) if r[1]), None)
        print("First sample:", rows[0][0][:40])
        print("Last sample:", rows[-1][0][:40])
        print("Earliest timestamp:", first_ts)
        print("Latest timestamp:", last_ts)

    if args.dry_run:
        print("Dry run: no rows written")
        return

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            for i in range(0, len(rows), args.batch_size):
                batch = rows[i : i + args.batch_size]
                cur.executemany(
                    "INSERT INTO nmea_data (nmea, timestamp) VALUES (%s, %s)",
                    batch,
                )
        conn.commit()
    finally:
        conn.close()

    print(f"Inserted: {len(rows)} rows into nmea_data")


if __name__ == "__main__":
    main()