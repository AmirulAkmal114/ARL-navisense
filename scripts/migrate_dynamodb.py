import os
import secrets
import sys
from datetime import datetime, timezone

import boto3
import psycopg2

DDB_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
USERS_TABLE = os.environ.get("DDB_USERS_TABLE", "Users")
NMEA_TABLE = os.environ.get("DDB_NMEA_TABLE", "NMEAData")
DATABASE_URL = os.environ.get("SUPABASE_DATABASE_URL")

BATCH_SIZE = 500


def parse_ts(value):
    if not value:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    s = str(value)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def scan_all(table):
    items = []
    resp = table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items


def migrate_users(ddb, conn):
    users = scan_all(ddb.Table(USERS_TABLE))
    print(f"Found {len(users)} users in DynamoDB")

    with conn.cursor() as cur:
        for u in users:
            email = u.get("Email") or u.get("email")
            if not email:
                continue

            token = u.get("Auth_Token") or secrets.token_hex(32)
            created = parse_ts(u.get("Time_Created"))
            expiry = parse_ts(u.get("Time_Expiry"))

            cur.execute(
                """
                INSERT INTO users
                    (email, first_name, last_name, organization, password_hash,
                     auth_token, time_created, time_expiry, package)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    organization = EXCLUDED.organization,
                    password_hash = EXCLUDED.password_hash,
                    auth_token = EXCLUDED.auth_token,
                    time_created = EXCLUDED.time_created,
                    time_expiry = EXCLUDED.time_expiry,
                    package = EXCLUDED.package
                """,
                (
                    email,
                    u.get("FirstName"),
                    u.get("LastName"),
                    u.get("Organization"),
                    u.get("PasswordHash"),
                    token,
                    created,
                    expiry,
                    u.get("Package"),
                ),
            )
    conn.commit()
    print("Users migrated")


def migrate_nmea(ddb, conn):
    items = scan_all(ddb.Table(NMEA_TABLE))
    print(f"Found {len(items)} NMEA records in DynamoDB")

    rows = []
    with conn.cursor() as cur:
        for item in items:
            nmea = item.get("nmea")
            if not nmea:
                continue
            rows.append((nmea, parse_ts(item.get("timestamp"))))

            if len(rows) >= BATCH_SIZE:
                cur.executemany(
                    "INSERT INTO nmea_data (nmea, timestamp) VALUES (%s, %s)",
                    rows,
                )
                rows = []

        if rows:
            cur.executemany(
                "INSERT INTO nmea_data (nmea, timestamp) VALUES (%s, %s)",
                rows,
            )
    conn.commit()
    print("NMEA data migrated")


def main():
    if not DATABASE_URL:
        print("SUPABASE_DATABASE_URL is not set")
        sys.exit(1)

    ddb = boto3.resource("dynamodb", region_name=DDB_REGION)
    conn = psycopg2.connect(DATABASE_URL)

    try:
        migrate_users(ddb, conn)
        migrate_nmea(ddb, conn)
    finally:
        conn.close()

    print("Migration complete")


if __name__ == "__main__":
    main()
