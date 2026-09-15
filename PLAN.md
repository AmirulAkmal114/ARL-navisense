# NaviSense — Current Phase & Plan

## Where we are

**Phase: Final integration & production hardening (feature-complete, pre-launch).**

The platform is built; what remains is verification, cleanup, and go-live.

Completed:
- Backend rebuilt on Vercel + Supabase (FastAPI) — all endpoints live (`all`, `class`, `time`, `mmsi`, `coordinate`, duration variants, `port/pagination`, `ingest`, `insert_ais_data`, `login`, `demo-request`, `health`)
- AIS decoder covers message types 1/2/3, 4, 5, 6, 7, 8, 10, 15, 18, 19, 24 + MID country lookup
- Supabase schema + seed data (`supabase/schema.sql`, `supabase/seed.sql`)
- DynamoDB -> Supabase data migration (done; `scripts/migrate_dynamodb.py` kept as reference)
- Frontend dashboard complete (login, map, port directory, profile)
- Vercel deployment wired (`vercel.json`, `api/index.py`, static mount)

## Plan

### 1. Migration cleanup + commit
- `requirements.txt`: remove duplicated `boto3` lines (server doesn't need it; `migrate_dynamodb.py` kept as a reference/rerun tool), fix missing trailing newline
- Commit in repo style (e.g. `Keep migration script as reference; drop boto3 from requirements`)

### 2. Verify migration ran correctly (read-only, secrets never printed)
- Counts: `nmea_data` (>= 5), `users` (>= 1), `ports` (8), `ais_data_sat`
- Quality: rows with NULL/empty `nmea` or NULL `timestamp`
- Sample latest 5 rows to confirm they decode and are time-sorted

### 3. Live ingest / device E2E testing
- Run uvicorn locally; test `/api/ingest` with `x-api-key`:
  - single NMEA + array `data` -> saved to `nmea_data`
  - sensor-only (`voltage`/`temperature`) -> saved to `sensor_data`
  - negatives: bad key -> 401, bad timestamp -> 422, empty body -> 400
- Test `POST /api/insert_ais_data` (nmea -> `ais_data_sat`)
- Repeat ingest smoke test against deployed Vercel URL; confirm `INGEST_API_KEY` is set in Vercel env

### 4. Frontend polish
- Rebrand titles: `port.html` + `profile.html` ("ARL AIS Dashboard" -> "NaviSense"), `map-embed.html` ("AIS Data Map" -> "NaviSense"), leftover "FleetEye/EarthView" text in `profile.html`
- Fix dead nav links (`About`/`Service`/`Contact`/`Forgot Password` are `href="#"`): wire to `map.html`/`port.html` or remove
- Re-enable or remove the commented-out Login button in `index.html`

## Deferred
- Consolidating `map.html` vs `map-embed.html` (~3,000-line near-duplicates) — risky, deferred