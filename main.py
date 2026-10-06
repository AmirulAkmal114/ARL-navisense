import hashlib
import os
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from math import radians, sin, cos, asin, sqrt

import bcrypt
from dateutil.parser import isoparse
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import ais_decoder
from backend.db import (
    count_ports,
    distinct_mmsi,
    get_nmea_rows,
    get_nmea_since,
    get_user_by_email,
    get_user_by_token,
    insert_ais,
    insert_nmea,
    insert_sensor,
    latest_ais_timestamp,
    list_ports,
    update_user_token,
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

app = FastAPI(title="NaviSense API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_ROWS = 5000


def utc_now():
    return datetime.now(timezone.utc)


def to_utc_naive(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def parse_dt(value):
    dt = isoparse(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * asin(sqrt(a))


def decode_item(item):
    line = item["nmea"]
    if not line or not line.startswith("!AIVDM"):
        return None

    parts = line.split(",")
    if len(parts) < 6:
        return None

    try:
        bitstring = ais_decoder.nmea_payload_to_bitstring(parts[5])
        decoded = ais_decoder.decode_ais(bitstring)
    except Exception:
        return None

    if "message_type" in decoded and "type" not in decoded:
        decoded["type"] = decoded["message_type"]
    if "country" not in decoded and decoded.get("mmsi") is not None:
        decoded["country"] = ais_decoder.get_country_from_mmsi(decoded["mmsi"])
    decoded.setdefault("channel", "A")

    decoded["raw"] = line

    ts = item.get("timestamp")
    if ts:
        try:
            dt = to_utc_naive(ts)
            decoded["unix_timestamp"] = int(dt.timestamp())
            decoded["datetime"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    return decoded


def fetch_nmea_rows(from_time=None, to_time=None, limit=MAX_ROWS):
    return get_nmea_rows(from_time=from_time, to_time=to_time, limit=limit)


def decode_rows(rows, mmsi=None, lat=None, lon=None, radius_km=None):
    decoded_messages = []
    skipped_messages = 0

    for item in rows:
        decoded = decode_item(item)
        if decoded is None:
            skipped_messages += 1
            continue

        if mmsi is not None and str(decoded.get("mmsi", "")) != str(mmsi):
            skipped_messages += 1
            continue

        if lat is not None and lon is not None and radius_km is not None:
            dlat = decoded.get("lat")
            dlon = decoded.get("lon")
            if dlat is None or dlon is None:
                skipped_messages += 1
                continue
            if haversine(float(lat), float(lon), float(dlat), float(dlon)) > radius_km:
                skipped_messages += 1
                continue

        decoded_messages.append(decoded)

    return decoded_messages, skipped_messages


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/_diag")
async def _diag():
    import socket
    import urllib.request

    info = {
        "has_postgrest_url": bool(os.environ.get("POSTGREST_URL")),
        "has_postgrest_jwt": bool(os.environ.get("POSTGREST_JWT")),
        "postgrest_host": os.environ.get("POSTGREST_URL", "").split("//")[-1],
        "code": "postgrest",
    }

    host = os.environ.get("POSTGREST_URL", "").split("//")[-1].split("/")[0]
    try:
        info["addrinfo"] = sorted({ai[4][0] for ai in socket.getaddrinfo(host, 443)})
    except Exception as exc:  # noqa: BLE001
        info["addrinfo_err"] = f"{type(exc).__name__}: {exc}"

    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=10) as resp:
            info["urllib_generic"] = resp.status
    except Exception as exc:  # noqa: BLE001
        info["urllib_generic_err"] = f"{type(exc).__name__}: {exc}"

    try:
        import httpx
        info["httpx_generic"] = httpx.get("https://api.ipify.org", timeout=10).status_code
    except Exception as exc:  # noqa: BLE001
        info["httpx_generic_err"] = f"{type(exc).__name__}: {exc}"

    try:
        sock = socket.create_connection((host, 443), timeout=10)
        sock.close()
        info["tcp_connect"] = "ok"
    except Exception as exc:  # noqa: BLE001
        info["tcp_connect_err"] = f"{type(exc).__name__}: {exc}"

    pg_url = os.environ.get("POSTGREST_URL", "").rstrip("/")
    jwt = os.environ.get("POSTGREST_JWT", "")
    req = urllib.request.Request(
        pg_url + "/ports?limit=1", headers={"Authorization": f"Bearer {jwt}", "apikey": jwt}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            info["urllib_pg"] = resp.status
    except Exception as exc:  # noqa: BLE001
        info["urllib_pg_err"] = f"{type(exc).__name__}: {exc}"

    try:
        import httpx
        info["httpx_pg"] = httpx.get(
            pg_url + "/ports?limit=1",
            headers={"Authorization": f"Bearer {jwt}", "apikey": jwt},
            timeout=10,
            trust_env=False,
        ).status_code
    except Exception as exc:  # noqa: BLE001
        info["httpx_pg_err"] = f"{type(exc).__name__}: {exc}"

    try:
        from backend import db as _db
        info["ports"] = _db.count_ports()
        info["ok"] = True
    except Exception as exc:  # noqa: BLE001
        info["ok"] = False
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


@app.post("/api/login")
async def login(request: Request):
    body = await request.json()
    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    stored = user.get("password_hash") or ""
    if stored.startswith("$2"):
        password_ok = bcrypt.checkpw(password.encode(), stored.encode())
    else:
        password_ok = hashlib.sha256(password.encode()).hexdigest() == stored

    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = user.get("auth_token")
    time_created = user.get("time_created")
    time_expiry = user.get("time_expiry")

    now = utc_now()
    refresh = not token
    if time_expiry and time_expiry < now:
        refresh = True

    if refresh:
        token = secrets.token_hex(32)
        time_created = now
        time_expiry = now + timedelta(days=30)
        update_user_token(email, token, time_created, time_expiry)

    return {
        "message": "Login successful",
        "user_info": [{
            "FirstName": user.get("first_name"),
            "LastName": user.get("last_name"),
            "Organization": user.get("organization"),
            "Email": user.get("email"),
            "Auth_Token": token,
            "Time_Created": time_created.isoformat() if time_created else None,
            "Time_Expiry": time_expiry.isoformat() if time_expiry else None,
            "Package": user.get("package")
        }]
    }


@app.get("/api/login")
async def validate_token(request: Request, token: str = Query(None)):
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized Token")

    time_expiry = user.get("time_expiry")
    if time_expiry and time_expiry < utc_now():
        raise HTTPException(status_code=401, detail="Unauthorized Token")

    return {
        "Username": f"{user.get('first_name') or ''} {user.get('last_name') or ''}".strip(),
        "Email": user.get("email")
    }


@app.get("/api/decode")
async def get_raw_nmea():
    rows = fetch_nmea_rows()
    nmea_list = [item["nmea"] for item in rows]
    return {
        "Number of NMEA messages": len(nmea_list),
        "NMEA": nmea_list
    }


@app.get("/api/all")
async def get_decoded_all():
    rows = fetch_nmea_rows()
    decoded_messages, skipped_messages = decode_rows(rows)
    return {
        "Decoded Messages": len(decoded_messages),
        "Skipped Messages": skipped_messages,
        "Decoded": decoded_messages
    }


@app.get("/api/class")
async def get_by_class(vessel_class: str = Query(...)):
    vclass = vessel_class.upper()
    if vclass not in ("A", "B"):
        raise HTTPException(status_code=422, detail="vessel_class must be A or B")

    allowed_types = [1, 2, 3] if vclass == "A" else [18, 19, 24]

    rows = fetch_nmea_rows()
    decoded_messages = []
    skipped_messages = 0

    for item in rows:
        decoded = decode_item(item)
        if decoded is None:
            skipped_messages += 1
            continue
        if decoded.get("type") not in allowed_types:
            skipped_messages += 1
            continue
        decoded_messages.append(decoded)

    return {
        "Vessel Class": vclass,
        "Decoded Messages": len(decoded_messages),
        "Skipped Messages": skipped_messages,
        "Decoded": decoded_messages
    }


@app.get("/api/time")
async def filter_by_time(from_time: str = None, to_time: str = None):
    try:
        from_dt = parse_dt(from_time) if from_time else None
        to_dt = parse_dt(to_time) if to_time else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid timestamp format")

    rows = fetch_nmea_rows(from_time=from_dt, to_time=to_dt)
    decoded_messages, skipped_messages = decode_rows(rows)

    return {
        "From": from_time,
        "To": to_time,
        "Decoded Messages": len(decoded_messages),
        "Skipped Messages": skipped_messages,
        "Decoded": decoded_messages
    }


@app.get("/api/mmsi")
async def get_by_mmsi(mmsi: str):
    rows = fetch_nmea_rows()
    decoded_messages, _ = decode_rows(rows, mmsi=mmsi)
    if not decoded_messages:
        raise HTTPException(status_code=404, detail="MMSI not found")
    return {"Number of Messages": len(decoded_messages), "Decoded": decoded_messages}


@app.get("/api/coordinate")
async def get_by_coordinate(lat: float, lon: float, radius_km: float = 100):
    rows = fetch_nmea_rows(limit=3000)
    decoded_messages, _ = decode_rows(rows, lat=lat, lon=lon, radius_km=radius_km)
    return {"Number of Messages": len(decoded_messages), "Decoded": decoded_messages}


@app.get("/api/get-by-mmsi/duration")
async def get_by_mmsi_duration(mmsi: str, from_time: str = None, to_time: str = None):
    try:
        from_dt = parse_dt(from_time) if from_time else None
        to_dt = parse_dt(to_time) if to_time else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid timestamp format")

    rows = fetch_nmea_rows(from_time=from_dt, to_time=to_dt)
    decoded_messages, _ = decode_rows(rows, mmsi=mmsi)
    return {"Number of Messages": len(decoded_messages), "Decoded": decoded_messages}


@app.get("/api/get-by-coordinate/duration")
async def get_by_coordinate_duration(lat: float, lon: float, from_time: str = None, to_time: str = None, radius_km: float = 100):
    try:
        from_dt = parse_dt(from_time) if from_time else None
        to_dt = parse_dt(to_time) if to_time else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid timestamp format")

    rows = fetch_nmea_rows(from_time=from_dt, to_time=to_dt)
    decoded_messages, _ = decode_rows(rows, lat=lat, lon=lon, radius_km=radius_km)
    return {"Number of Messages": len(decoded_messages), "Decoded": decoded_messages}


@app.get("/api/port/pagination")
async def port_pagination(page: int = Query(1, ge=1), page_size: int = Query(15, ge=1, le=100)):
    total_items = count_ports()

    offset = (page - 1) * page_size
    rows = list_ports(page_size, offset)

    data = []
    for row in rows:
        data.append({
            "country": row["country"],
            "locode": row["locode"],
            "port": row["port"],
            "latitude": float(row["latitude"]) if row["latitude"] is not None else None,
            "longitude": float(row["longitude"]) if row["longitude"] is not None else None,
        })

    return {"page": page, "page_size": page_size, "total_items": total_items, "data": data}


@app.post("/api/ingest")
async def ingest_nmea(request: Request):
    api_key = request.headers.get("x-api-key", "")
    expected_key = os.environ.get("INGEST_API_KEY", "")
    if not expected_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    body = await request.json()

    ts = None
    if body.get("timestamp"):
        try:
            ts = parse_dt(body["timestamp"])
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid timestamp format")

    nmea = body.get("nmea")
    raw_data = body.get("data") or []
    device_id = body.get("device_id")
    voltage = body.get("voltage")
    temperature = body.get("temperature")

    messages = []
    if nmea:
        messages.append(nmea)
    if isinstance(raw_data, list):
        for msg in raw_data:
            msg = (msg or "").strip()
            if msg:
                messages.append(msg)

    if messages:
        rows = [(msg, ts or utc_now()) for msg in messages]
        count = insert_nmea(rows)
        return {"status": "success", "saved": count, "table": "nmea_data"}

    if voltage is not None or temperature is not None:
        insert_sensor(device_id, voltage, temperature, ts or utc_now())
        return {"status": "success", "saved": 1, "table": "sensor_data"}

    raise HTTPException(status_code=400, detail="No NMEA messages or sensor values provided")


@app.post("/api/insert_ais_data")
async def insert_ais_data(limit: int = Query(1000, ge=1, le=5000)):
    since = latest_ais_timestamp() or datetime(1970, 1, 1, tzinfo=timezone.utc)

    rows = get_nmea_since(since, limit)

    if not rows:
        return {
            "message": "No new AIS data to archive",
            "inserted": 0,
            "inserted_mmsi": [],
            "all_mmsi_in_table": distinct_mmsi(),
        }

    archive_rows = []
    inserted_mmsi = []
    for row in rows:
        line = row["nmea"]
        mmsi = None
        try:
            if line and line.startswith("!AIVDM"):
                parts = line.split(",")
                if len(parts) >= 6:
                    bitstring = ais_decoder.nmea_payload_to_bitstring(parts[5])
                    decoded = ais_decoder.decode_ais(bitstring)
                    if decoded.get("mmsi") is not None:
                        mmsi = str(decoded["mmsi"])
        except Exception:
            mmsi = None

        archive_rows.append((row["timestamp"], 1, 2, 101, line, mmsi))
        if mmsi and mmsi not in inserted_mmsi:
            inserted_mmsi.append(mmsi)

    inserted = insert_ais(archive_rows)

    return {
        "message": "AIS data inserted successfully",
        "inserted": inserted,
        "inserted_mmsi": inserted_mmsi,
        "all_mmsi_in_table": distinct_mmsi(),
    }


@app.post("/api/demo-request")
async def demo_request(request: Request):
    body = await request.json()

    smtp_server = os.environ.get("SMTP_SERVER", "smtp.hostinger.com")
    try:
        smtp_port = int(os.environ.get("SMTP_PORT", "587") or "587")
    except ValueError:
        smtp_port = 587
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    admin_emails = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]

    if not smtp_user or not smtp_password or not admin_emails:
        raise HTTPException(status_code=500, detail="SMTP is not configured")

    text = (
        "New demo request:\n\n"
        f"Name: {body.get('first_name')} {body.get('last_name')}\n"
        f"Organization: {body.get('organization')}\n"
        f"Email: {body.get('email')}"
    )

    msg = MIMEText(text)
    msg["Subject"] = "New Demo Request"
    msg["From"] = smtp_user
    msg["To"] = ", ".join(admin_emails)

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, admin_emails, msg.as_string())
    except Exception as e:
        print("EMAIL ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"status": "success"}


if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
