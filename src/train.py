"""Training and MLflow experiment tracking for TempCast Malang LK-06."""

from pathlib import Path

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
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
EXPERIMENT_NAME = "TempCast-Malang-LK06-Final"

FEATURE_COLUMNS = [
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
    """Load raw weather data and create time-series features."""
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

    dataframe = dataframe.reset_index(drop=True)

    return dataframe


def chronological_split(
    dataframe: pd.DataFrame,
    train_ratio: float = 0.8,
):
    """Split time-series data chronologically."""
    split_index = int(len(dataframe) * train_ratio)

    train_data = dataframe.iloc[:split_index]
    test_data = dataframe.iloc[split_index:]

    x_train = train_data[FEATURE_COLUMNS]
    y_train = train_data[TARGET_COLUMN]

    x_test = test_data[FEATURE_COLUMNS]
    y_test = test_data[TARGET_COLUMN]

    return x_train, x_test, y_train, y_test


def evaluate_model(
    model,
    x_test: pd.DataFrame,
    y_test: pd.Series,
):
    """Calculate MAE, RMSE, and R2."""
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

    return mae, rmse, r2


def run_experiment(
    run_name,
    model,
    model_type,
    model_params,
    x_train,
    x_test,
    y_train,
    y_test,
):
    """Train one model and log its experiment to MLflow."""
    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param(
            "model_type",
            model_type,
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
            "train_ratio",
            0.8,
        )

        mlflow.log_param(
            "feature_count",
            len(FEATURE_COLUMNS),
        )

        for parameter_name, parameter_value in model_params.items():
            mlflow.log_param(
                parameter_name,
                parameter_value,
            )

        model.fit(
            x_train,
            y_train,
        )

        mae, rmse, r2 = evaluate_model(
            model,
            x_test,
            y_test,
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
        )

        print()
        print(f"Run: {run_name}")
        print(f"Model: {model_type}")
        print(f"MAE: {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2: {r2:.4f}")

        return {
            "run_id": run.info.run_id,
            "run_name": run_name,
            "model_type": model_type,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
        }


def main() -> None:
    """Run all LK-06 experiments."""
    mlflow.set_tracking_uri(TRACKING_URI)

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )

    dataframe = load_and_prepare_data()

    print("TempCast Malang - LK06")
    print(
        "Rows after feature engineering:",
        len(dataframe),
    )

    (
        x_train,
        x_test,
        y_train,
        y_test,
    ) = chronological_split(
        dataframe
    )

    print(
        "Training rows:",
        len(x_train),
    )

    print(
        "Testing rows:",
        len(x_test),
    )

    experiments = [
        {
            "run_name": "linear_regression_baseline",
            "model": LinearRegression(),
            "model_type": "LinearRegression",
            "params": {},
        },
        {
            "run_name": "random_forest_100_depth_5",
            "model": RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42,
            ),
            "model_type": "RandomForestRegressor",
            "params": {
                "n_estimators": 100,
                "max_depth": 5,
                "random_state": 42,
            },
        },
        {
            "run_name": "random_forest_200_depth_10",
            "model": RandomForestRegressor(
                n_estimators=200,
                max_depth=10,
                random_state=42,
            ),
            "model_type": "RandomForestRegressor",
            "params": {
                "n_estimators": 200,
                "max_depth": 10,
                "random_state": 42,
            },
        },
        {
            "run_name": "random_forest_300_unlimited",
            "model": RandomForestRegressor(
                n_estimators=300,
                max_depth=None,
                random_state=42,
            ),
            "model_type": "RandomForestRegressor",
            "params": {
                "n_estimators": 300,
                "max_depth": "None",
                "random_state": 42,
            },
        },
    ]

    results = []

    for experiment in experiments:
        result = run_experiment(
            run_name=experiment["run_name"],
            model=experiment["model"],
            model_type=experiment["model_type"],
            model_params=experiment["params"],
            x_train=x_train,
            x_test=x_test,
            y_train=y_train,
            y_test=y_test,
        )

        results.append(result)

    result_dataframe = pd.DataFrame(results)

    result_dataframe = result_dataframe.sort_values(
        "rmse",
        ascending=True,
    ).reset_index(drop=True)

    print()
    print("Experiment Comparison")
    print(
        result_dataframe[
            [
                "run_name",
                "model_type",
                "mae",
                "rmse",
                "r2",
            ]
        ].to_string(
            index=False
        )
    )

    best_result = result_dataframe.iloc[0]

    print()
    print("Best Model")
    print(
        "Run:",
        best_result["run_name"],
    )
    print(
        "Model:",
        best_result["model_type"],
    )
    print(
        f"MAE: {best_result['mae']:.4f}"
    )
    print(
        f"RMSE: {best_result['rmse']:.4f}"
    )
    print(
        f"R2: {best_result['r2']:.4f}"
    )

    result_dataframe.to_csv(
        "lk06_experiment_results.csv",
        index=False,
    )

    print()
    print(
        "Experiment summary saved to:",
        "lk06_experiment_results.csv",
    )


if __name__ == "__main__":
    main()