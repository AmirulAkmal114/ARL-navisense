# Raspberry Pi Database Mirror (NaviSense)

The NaviSense app keeps Supabase as its primary cloud database. When
`PI_DATABASE_URL` is set, every write is also mirrored to a PostgreSQL
database running on the Raspberry Pi, reached through a Cloudflare Tunnel.
If the Pi is unreachable, mirror errors are logged and ignored — the cloud app
never breaks because of the Pi.

## 1. Install PostgreSQL on the Pi

```bash
sudo apt update
sudo apt install -y postgresql
sudo systemctl enable --now postgresql
```

PostgreSQL listens on `localhost:5432` only — exactly what we want, since the
tunnel connects locally.

## 2. Create the NaviSense database

Copy `scripts/setup_pi_db.sql` to the Pi and run it as the postgres superuser:

```bash
scp scripts/setup_pi_db.sql pi@<pi-host>:/tmp/
ssh pi@<pi-host> "sudo -u postgres psql -f /tmp/setup_pi_db.sql"
```

Edit the file first and change `CHANGE-ME-strong-password` to a real password.

## 3. Expose Postgres with a Cloudflare Tunnel

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
  - hostname: pi-db.yourdomain.com
    service: tcp://localhost:5432
  - service: http_status:404
```

Then route the hostname and run it as a service:

```bash
cloudflared tunnel route dns navisense-pi-db pi-db.yourdomain.com
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

### Quick test without a domain

```bash
cloudflared tunnel --url tcp://localhost:5432
```

This prints a random `*.trycloudflare.com` URL you can use in step 4 to test,
but it changes on every restart — use a real hostname for production.

## 4. Configure the app

Add to `.env` (local) and to the Vercel environment variables:

```
PI_DATABASE_URL=postgresql://navisense:<password>@pi-db.yourdomain.com:5432/navisense
```

From now on every `INSERT`/`UPDATE` the app performs is mirrored to the Pi.

## 5. Backfill existing data

One-time (or repeatable) copy of existing Supabase rows to the Pi:

```bash
python scripts/pi_backfill.py          # incremental: only rows newer than the Pi's watermark
python scripts/pi_backfill.py --full   # everything (conflicts are skipped)
```

## 6. Verify

```bash
# On the Pi
sudo -u postgres psql -d navisense -c "select count(*) from nmea_data;"
```

Or from your dev machine with `psql` pointed at `PI_DATABASE_URL`.
