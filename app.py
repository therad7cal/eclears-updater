import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
import random

import requests
import scratchattach as scratch3
from flask import Flask, jsonify

app = Flask(__name__)

STATE_FILE = os.getenv("STATE_FILE", "tracker_state.json")
API_URL = os.getenv("API_URL", "https://tgrcode.com/mm2/user_info/HQ6-63D-94G")
SCRATCH_USERNAME = os.environ["SCRATCH_USERNAME"]
SCRATCH_PASSWORD = os.environ["SCRATCH_PASSWORD"]
PROJECT_ID = int(os.getenv("PROJECT_ID", "1363601841"))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "60"))


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"previous_score": None, "previous_time": None}


def save_state(score, timestamp):
    temporary_file = f"{STATE_FILE}.tmp"
    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump({"previous_score": score, "previous_time": timestamp}, file)
    os.replace(temporary_file, STATE_FILE)


def run_updater():
    state = load_state()
    previous_score = state.get("previous_score")
    previous_time = state.get("previous_time")
    http = requests.Session()
    http.headers.update({"User-Agent": "eclears-updater/1.0"})

    while True:
        try:
            # Reconnect if Scratch or the network drops.
            scratch_session = scratch3.login(SCRATCH_USERNAME, SCRATCH_PASSWORD)
            connection = scratch_session.connect_cloud(PROJECT_ID)
            log.info("Connected to Scratch cloud project %s", PROJECT_ID)

            while True:
                response = http.get(API_URL, timeout=15)
                response.raise_for_status()
                data = response.json()
                global eclears
                global totalclears
                global rate_per_hour
                eclears = int(data.get("expert_highscore", 0))
                totalclears = int(data.get("courses_cleared", 0))
                current_time = time.time()
                rate_per_hour = 0

                if previous_score is not None and previous_time is not None:
                    elapsed_hours = (current_time - previous_time) / 3600
                    if elapsed_hours > 0:
                        rate_per_hour = (eclears - previous_score) / elapsed_hours

                previous_score = eclears
                previous_time = current_time
                save_state(previous_score, previous_time)

                connection.set_var("ECLEARS", eclears)
                connection.set_var("TOTALCLEARS", totalclears)
                connection.set_var("PERHOUR", int(round(rate_per_hour)))
                log.info("Updated ECLEARS=%s TOTALCLEARS=%s PERHOUR=%s", eclears, totalclears, int(round(rate_per_hour)))
                time.sleep(UPDATE_INTERVAL)

        except Exception:
            log.exception("Updater failed; retrying in 15 seconds")
            time.sleep(15)


@app.get("/")
def home():
    return jsonify({"expert_clears": eclears, "totalclears": totalclears, "rate": rate_per_hour, "sessioncookiethingyOwO": random.randint(100000,999999)})
    
@app.get("/uwuimsogayyy")
def home():
    return jsonify({"OwO": "UwU"})


@app.get("/health")
def health():
    return jsonify({"status": "alive", "time": datetime.now(timezone.utc).isoformat()})


if __name__ == "__main__":
    threading.Thread(target=run_updater, daemon=True).start()
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
