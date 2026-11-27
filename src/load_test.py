"""LK-11 workload simulation for TempCast Malang."""

import random
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from collections import Counter

import requests

DURATION = 180
WORKERS = 3

replica_ips = sorted({
    item[4][0]
    for item in socket.getaddrinfo(
        "model-serving",
        8080,
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
})

print("Discovered replicas:", replica_ips)


def generate_payload():
    temperature = random.uniform(23, 28)

    return {
        "temperature_2m_min": temperature - 4,
        "temperature_2m_mean": temperature,
        "precipitation_sum": random.uniform(0, 5),
        "wind_speed_10m_max": random.uniform(8, 16),
        "temperature_2m_max_lag1": random.uniform(28, 34),
        "temperature_2m_max_lag3": random.uniform(28, 34),
        "temperature_2m_max_lag7": random.uniform(28, 34),
        "temperature_2m_max_roll3_mean": random.uniform(28, 34),
        "temperature_2m_max_roll7_mean": random.uniform(28, 34),
        "month": 11,
        "day_of_year": 322,
    }


def worker(ip, deadline):
    counts = Counter()
    url = f"http://{ip}:8080/invocations"

    while time.monotonic() < deadline:
        try:
            response = requests.post(
                url,
                json={
                    "dataframe_records": [
                        generate_payload()
                    ]
                },
                timeout=5,
            )

            if response.status_code == 200:
                result = response.json()
                replica = result.get("replica", ip)
                counts[replica] += 1
            else:
                counts["error"] += 1

        except requests.RequestException:
            counts["error"] += 1

        time.sleep(random.uniform(0.2, 0.6))

    return counts


if __name__ == "__main__":
    deadline = time.monotonic() + DURATION

    print("Starting workload simulation...")
    print("Duration:", DURATION, "seconds")

    total = Counter()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(worker, ip, deadline)
            for ip in replica_ips
        ]

        for future in futures:
            total.update(future.result())

    print("\n=== LOAD TEST RESULTS ===")

    for replica, count in total.items():
        print(replica, ":", count, "requests")

    print("Total successful requests:",
          sum(v for k, v in total.items() if k != "error"))

    print("Total errors:", total["error"])