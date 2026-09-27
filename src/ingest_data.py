"""Dynamic data ingestion for TempCast Malang."""

import time
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"

LATITUDE = -7.98
LONGITUDE = 112.63
TIMEZONE = "Asia/Jakarta"

WINDOW_DAYS = 550
ARCHIVE_LAG_DAYS = 7

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

RAW_DATA_DIR = Path("data/raw")

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
]


def fetch_weather_data(
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    """Fetch daily weather data from Open-Meteo."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": TIMEZONE,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            payload = response.json()

            if "daily" not in payload:
                raise ValueError(
                    "API response does not contain daily data."
                )

            dataframe = pd.DataFrame(
                payload["daily"]
            )

            if dataframe.empty:
                raise ValueError(
                    "API returned an empty dataset."
                )

            print(
                f"HTTP Status: {response.status_code}"
            )
            print(
                f"Rows received: {len(dataframe)}"
            )

            return dataframe

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            print(
                f"Attempt {attempt}/"
                f"{MAX_RETRIES} failed: {error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(
                    RETRY_DELAY_SECONDS
                )

    raise RuntimeError(
        "Unable to retrieve weather data."
    )


def save_raw_data(
    dataframe: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> Path:
    """Save raw data using a timestamped filename."""
    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        ZoneInfo(TIMEZONE)
    ).strftime("%Y%m%d_%H%M%S")

    filename = (
        f"weather_{start_date.isoformat()}_"
        f"to_{end_date.isoformat()}_"
        f"{timestamp}.csv"
    )

    output_path = (
        RAW_DATA_DIR / filename
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )

    return output_path


def main() -> None:
    """Run the ingestion process."""
    end_date = (
        date.today()
        - timedelta(
            days=ARCHIVE_LAG_DAYS
        )
    )

    start_date = (
        end_date
        - timedelta(
            days=WINDOW_DAYS - 1
        )
    )

    print(
        "TempCast Malang - Data Ingestion"
    )
    print(
        f"Requested period: "
        f"{start_date} to {end_date}"
    )

    dataframe = fetch_weather_data(
        start_date=start_date,
        end_date=end_date,
    )

    output_path = save_raw_data(
        dataframe=dataframe,
        start_date=start_date,
        end_date=end_date,
    )

    print(
        f"Raw data saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()