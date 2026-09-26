"""Preprocessing pipeline for TempCast Malang."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


TIMEZONE = "Asia/Jakarta"

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

REQUIRED_COLUMNS = [
    "time",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
]

NUMERIC_COLUMNS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
]


def load_raw_data() -> pd.DataFrame:
    """Load and combine all raw weather CSV files."""
    raw_files = sorted(
        RAW_DATA_DIR.glob("weather_*.csv")
    )

    if not raw_files:
        raise FileNotFoundError(
            "No raw weather files found in data/raw/."
        )

    dataframes = [
        pd.read_csv(file_path)
        for file_path in raw_files
    ]

    dataframe = pd.concat(
        dataframes,
        ignore_index=True,
    )

    print(f"Raw files loaded: {len(raw_files)}")
    print(f"Rows before preprocessing: {len(dataframe)}")

    return dataframe


def validate_columns(dataframe: pd.DataFrame) -> None:
    """Validate required columns."""
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def clean_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean timestamps, numeric values, missing values, and duplicates."""
    dataframe = dataframe.copy()

    validate_columns(dataframe)

    dataframe["time"] = pd.to_datetime(
        dataframe["time"],
        errors="coerce",
    )

    for column in NUMERIC_COLUMNS:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = dataframe.dropna(
        subset=REQUIRED_COLUMNS
    )

    dataframe = dataframe.sort_values("time")

    dataframe = dataframe.drop_duplicates(
        subset=["time"],
        keep="last",
    )

    dataframe = dataframe.reset_index(drop=True)

    return dataframe


def create_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Create time-series features."""
    dataframe = dataframe.copy()

    dataframe["temperature_2m_max_lag1"] = (
        dataframe["temperature_2m_max"].shift(1)
    )

    dataframe["temperature_2m_max_lag3"] = (
        dataframe["temperature_2m_max"].shift(3)
    )

    dataframe["temperature_2m_max_lag7"] = (
        dataframe["temperature_2m_max"].shift(7)
    )

    dataframe["temperature_2m_max_roll3_mean"] = (
        dataframe["temperature_2m_max"]
        .shift(1)
        .rolling(window=3)
        .mean()
    )

    dataframe["temperature_2m_max_roll7_mean"] = (
        dataframe["temperature_2m_max"]
        .shift(1)
        .rolling(window=7)
        .mean()
    )

    dataframe["month"] = dataframe["time"].dt.month
    dataframe["day_of_year"] = dataframe["time"].dt.dayofyear

    dataframe["temperature_2m_max_t_plus_1"] = (
        dataframe["temperature_2m_max"].shift(-1)
    )

    dataframe = dataframe.dropna().reset_index(drop=True)

    return dataframe


def save_processed_data(
    dataframe: pd.DataFrame,
) -> Path:
    """Save processed data with timestamped filename."""
    PROCESSED_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        ZoneInfo(TIMEZONE)
    ).strftime("%Y%m%d_%H%M%S")

    output_path = (
        PROCESSED_DATA_DIR
        / f"tempcast_features_{timestamp}.csv"
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )

    return output_path


def main() -> None:
    """Run the preprocessing pipeline."""
    dataframe = load_raw_data()

    dataframe = clean_data(dataframe)

    print(
        "Rows after cleaning:",
        len(dataframe),
    )

    dataframe = create_features(dataframe)

    print(
        "Rows after feature engineering:",
        len(dataframe),
    )

    output_path = save_processed_data(
        dataframe
    )

    print(
        f"Processed data saved to: {output_path}"
    )


if __name__ == "__main__":
    main()