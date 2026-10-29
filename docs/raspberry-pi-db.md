# Raspberry Pi Database + PostgREST (NaviSense)

NaviSense stores its data in PostgreSQL on the Raspberry Pi. The FastAPI app on
Vercel talks to it through PostgREST over HTTPS; it does not open a Postgres
connection directly.

Supabase is the legacy source. `scripts/pi_backfill.py` copies existing rows
into the Pi database, but the running app no longer reads from Supabase.

## 1. Install PostgreSQL on the Pi

```bash
sudo apt update
sudo apt install -y postgresql
sudo systemctl enable --now postgresql
```

PostgreSQL listens on `localhost:5432` only — exactly what we want, since
PostgREST and the tunnel connect locally.

## 2. Create the NaviSense database

Copy `scripts/setup_pi_db.sql` to the Pi and run it as the postgres superuser:

```bash
scp scripts/setup_pi_db.sql pi@<pi-host>:/tmp/
ssh pi@<pi-host> "sudo -u postgres psql -f /tmp/setup_pi_db.sql"
```

Edit the file first and change `CHANGE-ME-strong-password` to a real password.
The script creates the `navisense` database, all application tables, and the
`arl_app` role used by the PostgREST JWT.

## 3. Run PostgREST

PostgREST exposes the database as a REST API on port 3000. A Docker setup is
the simplest option:

```bash
docker run -d --name postgrest --restart unless-stopped --network host \
  -e PGRST_DB_URI="postgres://navisense:<password>@127.0.0.1:5432/navisense" \
  -e PGRST_DB_SCHEMAS=public \
  -e PGRST_JWT_SECRET="<jwt-secret>" \
  postgrest/postgrest
```

The JWT in `POSTGREST_JWT` must be signed with the same `<jwt-secret>` and
contain `"role": "arl_app"`.

## 4. Expose PostgREST with a Cloudflare Tunnel

On the Pi:

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

# Login and create a tunnel (needs a domain on your Cloudflare account)
cloudflared tunnel login
cloudflared tunnel create navisense-pi-db
```

In `~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL_ID from "cloudflared tunnel list">
credentials-file: /home/pi/.cloudflared/<TUNNEL_ID>.json

ingress:
  - hostname: db.arl-navisense.com
    service: http://localhost:3000
  - service: http_status:404
```

Then route the hostname and run it as a service:

```bash
cloudflared tunnel route dns navisense-pi-db db.arl-navisense.com
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

### Quick test without a domain

```bash
cloudflared tunnel --url http://localhost:3000
```

This prints a random `*.trycloudflare.com` URL you can use in step 5 to test,
but it changes on every restart — use a real hostname for production.

## 5. Configure the app

Add these to `.env` locally and to the Vercel environment variables
(Production and Preview):

```
POSTGREST_URL=https://db.arl-navisense.com
POSTGREST_JWT=<JWT signed with PGRST_JWT_SECRET, role=arl_app>
```

Restart the app after changing them. The app will return 500 on database
routes if either variable is missing or the JWT is rejected by PostgREST.

## 6. Backfill existing Supabase data

`PI_DATABASE_URL` is only needed by the backfill script; the app itself uses
PostgREST. Add both connection strings to `.env`:

```
SUPABASE_DATABASE_URL=postgresql://...
PI_DATABASE_URL=postgresql://navisense:<password>@<pi-host>:5432/navisense
```

Then run:

```bash
python scripts/pi_backfill.py          # incremental: only rows newer than the Pi's watermark
python scripts/pi_backfill.py --full   # everything (conflicts are skipped)
```

## 7. Verify

From your dev machine:

```bash
curl https://<vercel-app>/api/health
curl "https://<vercel-app>/api/port/pagination?page=1&page_size=1"
```

On the Pi:

```bash
sudo -u postgres psql -d navisense -c "select count(*) from nmea_data;"
```
