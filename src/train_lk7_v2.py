"""Train and register TempCast Malang model version 2 for LK-07."""

from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

DATA_FILE = Path(
    "data/raw/"
    "weather_2025-03-20_to_2026-09-20_20260927_224435.csv"
)

TRACKING_URI = "http://127.0.0.1:5000"
EXPERIMENT_NAME = "TempCast-Malang-LK07"
REGISTERED_MODEL_NAME = "TempCast-Malang-Best-Model"

FEATURE_COLUMNS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "temperature_2m_max_lag1",
    "temperature_2m_max_lag3",
    "temperature_2m_max_lag7",
    "temperature_2m_max_roll3_mean",
    "temperature_2m_max_roll7_mean",
    "month",
    "day_of_year",
]

TARGET_COLUMN = "temperature_2m_max_t_plus_1"


def load_and_prepare_data() -> pd.DataFrame:
    """Load weather data and create features for model version 2."""
    dataframe = pd.read_csv(DATA_FILE)

    dataframe["time"] = pd.to_datetime(
        dataframe["time"],
        errors="coerce",
    )

    numeric_columns = [
        "temperature_2m_max",
        "temperature_2m_min",
        "temperature_2m_mean",
        "precipitation_sum",
        "wind_speed_10m_max",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe = dataframe.dropna(
        subset=["time"] + numeric_columns
    )

    dataframe = dataframe.sort_values("time")

    dataframe = dataframe.drop_duplicates(
        subset=["time"],
        keep="last",
    )

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

    dataframe[TARGET_COLUMN] = (
        dataframe["temperature_2m_max"].shift(-1)
    )

    dataframe = dataframe.dropna(
        subset=FEATURE_COLUMNS + [TARGET_COLUMN]
    )

    return dataframe.reset_index(drop=True)


def main() -> None:
    """Train and register version 2."""
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)

    dataframe = load_and_prepare_data()

    split_index = int(len(dataframe) * 0.8)

    train_data = dataframe.iloc[:split_index]
    test_data = dataframe.iloc[split_index:]

    x_train = train_data[FEATURE_COLUMNS]
    y_train = train_data[TARGET_COLUMN]

    x_test = test_data[FEATURE_COLUMNS]
    y_test = test_data[TARGET_COLUMN]

    model = LinearRegression()

    with mlflow.start_run(
        run_name="linear_regression_v2_extra_current_temp"
    ):
        model.fit(x_train, y_train)

        predictions = model.predict(x_test)

        mae = mean_absolute_error(
            y_test,
            predictions,
        )

        rmse = np.sqrt(
            mean_squared_error(
                y_test,
                predictions,
            )
        )

        r2 = r2_score(
            y_test,
            predictions,
        )

        mlflow.log_param(
            "model_type",
            "LinearRegression",
        )

        mlflow.log_param(
            "model_version_candidate",
            "v2",
        )

        mlflow.log_param(
            "feature_count",
            len(FEATURE_COLUMNS),
        )

        mlflow.log_param(
            "train_rows",
            len(x_train),
        )

        mlflow.log_param(
            "test_rows",
            len(x_test),
        )

        mlflow.log_param(
            "change_from_v1",
            "add_temperature_2m_max_feature",
        )

        mlflow.log_metric(
            "mae",
            mae,
        )

        mlflow.log_metric(
            "rmse",
            rmse,
        )

        mlflow.log_metric(
            "r2",
            r2,
        )

        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            serialization_format="cloudpickle",
            registered_model_name=REGISTERED_MODEL_NAME,
        )

        print("TempCast Malang - LK07 Model V2")
        print(f"Training rows: {len(x_train)}")
        print(f"Testing rows: {len(x_test)}")
        print(f"Feature count: {len(FEATURE_COLUMNS)}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2: {r2:.4f}")
        print()
        print(
            "Registered model:",
            REGISTERED_MODEL_NAME,
        )
        print(
            "Expected registry version: v2"
        )


if __name__ == "__main__":
    main()
