import os
import time
import json
import requests
from collections import deque

# --- ENV CONFIG ---
LOG_FILE = "/var/log/nginx/access.log"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", 2.0))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 200))
ALERT_COOLDOWN_SEC = int(os.getenv("ALERT_COOLDOWN_SEC", 300))

# --- STATE ---
recent_statuses = deque(maxlen=WINDOW_SIZE)
last_alert_time = 0
last_pool_seen = None


def send_slack_alert(message: str):
    """Send message to Slack via webhook."""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ No Slack webhook configured.")
        return
    payload = {"text": message}
    try:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        print(f"✅ Sent alert: {message}")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")


def check_error_rate():
    """Compute 5xx error rate and alert if threshold exceeded."""
    global last_alert_time
    now = time.time()
    if len(recent_statuses) == 0:
        return

    errors = sum(1 for s in recent_statuses if s.startswith("5"))
    rate = (errors / len(recent_statuses)) * 100

    if rate > ERROR_RATE_THRESHOLD and (now - last_alert_time) > ALERT_COOLDOWN_SEC:
        send_slack_alert(f"🚨 High error rate detected! {rate:.2f}% over last {len(recent_statuses)} requests.")
        last_alert_time = now


def check_failover(pool):
    """Detect pool switch (blue -> green or vice versa)."""
    global last_pool_seen, last_alert_time
    now = time.time()
    if last_pool_seen is None:
        last_pool_seen = pool
        return

    if pool != last_pool_seen and (now - last_alert_time) > ALERT_COOLDOWN_SEC:
        send_slack_alert(f"🔄 Failover detected! Traffic switched from *{last_pool_seen}* → *{pool}*.")
        last_pool_seen = pool
        last_alert_time = now


def tail_logs():
    """Continuously read Nginx logs."""
    print("👀 Watching Nginx logs for failovers and errors...")

    # Wait until file exists
    while not os.path.exists(LOG_FILE):
        print("⏳ Waiting for Nginx log file...")
        time.sleep(2)

    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)  # start at the end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            parts = line.split()
            if len(parts) < 9:
                continue

            # Example log: pool=blue release=v1 upstream_status=200 ...
            pool = None
            status = None

            for p in parts:
                if p.startswith("pool="):
                    pool = p.split("=")[-1]
                if p.startswith("upstream_status="):
                    status = p.split("=")[-1]

            if status:
                recent_statuses.append(status)
                check_error_rate()
            if pool:
                check_failover(pool)


if __name__ == "__main__":
    try:
        tail_logs()
    except KeyboardInterrupt:
        print("🛑 Watcher stopped.")

