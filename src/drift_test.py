"""LK-11 controlled data drift simulation."""

import sys
import time
import random
import requests

MODE = sys.argv[1] if len(sys.argv) > 1 else "normal"

API_URL = "http://localhost:8000/predict"

BASELINE = {
    "temperature_2m_min": 21.0786,
    "temperature_2m_mean": 23.9836,
    "precipitation_sum": 8.3149,
    "wind_speed_10m_max": 8.5865,
    "temperature_2m_max_lag1": 28.6239,
    "temperature_2m_max_lag3": 28.6333,
    "temperature_2m_max_lag7": 28.6543,
    "temperature_2m_max_roll3_mean": 28.6298,
    "temperature_2m_max_roll7_mean": 28.6395,
    "month": 6,
    "day_of_year": 173,
}

if MODE not in ("normal", "drift"):
    raise ValueError("Mode must be normal or drift")

TOTAL_REQUESTS = 60 if MODE == "normal" else 120

success = 0
errors = 0

print("Simulation mode:", MODE)
print("Total requests:", TOTAL_REQUESTS)

for i in range(TOTAL_REQUESTS):
    payload = BASELINE.copy()

    for feature in payload:
        if feature not in ("month", "day_of_year"):
            payload[feature] *= random.uniform(0.98, 1.02)

    if MODE == "drift":
        payload["temperature_2m_min"] += 8
        payload["temperature_2m_mean"] += 8
        payload["temperature_2m_max_lag1"] += 8
        payload["temperature_2m_max_lag3"] += 8
        payload["temperature_2m_max_lag7"] += 8
        payload["temperature_2m_max_roll3_mean"] += 8
        payload["temperature_2m_max_roll7_mean"] += 8

    try:
        response = requests.post(
            API_URL,
            json=payload,
            timeout=10,
        )

        if response.status_code == 200:
            success += 1
        else:
            errors += 1

    except requests.RequestException:
        errors += 1

    time.sleep(0.3)

print("\n=== DRIFT SIMULATION RESULTS ===")
print("Mode:", MODE)
print("Successful requests:", success)
print("Errors:", errors)