"""PostgREST-backed data access for NaviSense.

Replaces the previous psycopg2 direct-Postgres implementation. All reads and
writes go through PostgREST over HTTPS using a JWT (a server-side secret).

Environment:
  POSTGREST_URL  e.g. https://db.example.com
  POSTGREST_JWT  HS256 JWT signed with the PostgREST jwt-secret (role=arl_app)
"""

import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE = os.environ.get("POSTGREST_URL", "").rstrip("/")
JWT = os.environ.get("POSTGREST_JWT", "")

_TIMESTAMP_FIELDS = {"timestamp", "time_stamp", "time_created", "time_expiry"}


def _headers(extra=None):
    if not BASE or not JWT:
        raise RuntimeError("POSTGREST_URL and POSTGREST_JWT must be set")
    headers = {
        "apikey": JWT,
        "Authorization": f"Bearer {JWT}",
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


def _client():
    return httpx.Client(base_url=BASE, headers=_headers(), timeout=30)


def _iso(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat()
    return value


def _parse_timestamps(row):
    for key in list(row.keys()):
        if key in _TIMESTAMP_FIELDS and isinstance(row[key], str):
            try:
                row[key] = datetime.fromisoformat(row[key].replace("Z", "+00:00"))
            except ValueError:
                pass
    return row


def _rows(response):
    response.raise_for_status()
    data = response.json()
    if isinstance(data, list):
        return [_parse_timestamps(row) for row in data]
    return _parse_timestamps(data)


# --- users -----------------------------------------------------------------

def get_user_by_email(email):
    with _client() as client:
        rows = _rows(client.get("/users", params={"email": f"eq.{email}", "limit": 1}))
        return rows[0] if rows else None


def get_user_by_token(token):
    with _client() as client:
        rows = _rows(client.get("/users", params={"auth_token": f"eq.{token}", "limit": 1}))
        return rows[0] if rows else None


def update_user_token(email, token, time_created, time_expiry):
    with _client() as client:
        client.patch(
            "/users",
            params={"email": f"eq.{email}"},
            json={
                "auth_token": token,
                "time_created": _iso(time_created),
                "time_expiry": _iso(time_expiry),
            },
        ).raise_for_status()


# --- nmea_data -------------------------------------------------------------

def get_nmea_rows(from_time=None, to_time=None, limit=5000, descending=True):
    params = {
        "select": "nmea,timestamp",
        "limit": limit,
        "order": "timestamp.desc.nullslast" if descending else "timestamp.asc",
    }
    conditions = []
    if from_time is not None:
        conditions.append(f"timestamp.gte.{_iso(from_time)}")
    if to_time is not None:
        conditions.append(f"timestamp.lte.{_iso(to_time)}")
    if conditions:
        params["and"] = f"({','.join(conditions)})"
    with _client() as client:
        return _rows(client.get("/nmea_data", params=params))


def insert_nmea(rows):
    payload = [{"nmea": nmea, "timestamp": _iso(ts)} for nmea, ts in rows]
    if not payload:
        return 0
    with _client() as client:
        client.post(
            "/nmea_data",
            json=payload,
            headers=_headers({"Prefer": "return=minimal"}),
        ).raise_for_status()
    return len(payload)


# --- sensor_data -----------------------------------------------------------

def insert_sensor(device_id, voltage, temperature, ts):
    with _client() as client:
        client.post(
            "/sensor_data",
            json={
                "device_id": device_id,
                "voltage": voltage,
                "temperature": temperature,
                "nmea": None,
                "timestamp": _iso(ts),
            },
            headers=_headers({"Prefer": "return=minimal"}),
        ).raise_for_status()
    return 1


# --- ports -----------------------------------------------------------------

def count_ports():
    with _client() as client:
        response = client.get(
            "/ports",
            params={"select": "locode", "limit": 1},
            headers=_headers({"Prefer": "count=exact"}),
        )
        response.raise_for_status()
        content_range = response.headers.get("content-range", "0-0/0")
        return int(content_range.split("/")[-1])


def list_ports(limit, offset):
    with _client() as client:
        return _rows(
            client.get(
                "/ports",
                params={
                    "select": "country,locode,port,latitude,longitude",
                    "order": "country.asc,locode.asc",
                    "limit": limit,
                    "offset": offset,
                },
            )
        )


# --- ais_data_sat ----------------------------------------------------------

def latest_ais_timestamp():
    with _client() as client:
        rows = _rows(
            client.get(
                "/ais_data_sat",
                params={"select": "time_stamp", "order": "time_stamp.desc.nullslast", "limit": 1},
            )
        )
        return rows[0]["time_stamp"] if rows else None


def get_nmea_since(since, limit):
    with _client() as client:
        return _rows(
            client.get(
                "/nmea_data",
                params={
                    "select": "nmea,timestamp",
                    "timestamp": f"gt.{_iso(since)}",
                    "order": "timestamp.asc",
                    "limit": limit,
                },
            )
        )


def distinct_mmsi():
    with _client() as client:
        rows = _rows(
            client.get("/ais_data_sat", params={"select": "mmsi", "mmsi": "not.is.null"})
        )
    seen = []
    for row in rows:
        value = row.get("mmsi")
        if value is not None and value not in seen:
            seen.append(value)
    return seen


def insert_ais(rows):
    payload = [
        {
            "time_stamp": _iso(ts),
            "ch1": ch1,
            "ch2": ch2,
            "rssi": rssi,
            "data_column": line,
            "mmsi": mmsi,
        }
        for ts, ch1, ch2, rssi, line, mmsi in rows
    ]
    if not payload:
        return 0
    with _client() as client:
        client.post(
            "/ais_data_sat",
            json=payload,
            headers=_headers({"Prefer": "return=minimal"}),
        ).raise_for_status()
    return len(payload)
