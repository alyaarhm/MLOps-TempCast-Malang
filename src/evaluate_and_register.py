"""Automated model validation and MLflow registry update for LK-08."""

import os
import sys

import mlflow
import pandas as pd
from mlflow.tracking import MlflowClient


RESULT_FILE = "lk06_experiment_results.csv"

TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

REGISTERED_MODEL_NAME = "TempCast-Malang-Best-Model"

# LK-01 baseline MAE = 0.8297.
# Model baru masih dianggap layak bila penurunan performa tidak lebih dari 20%.
BASELINE_MAE = 0.8297
MAX_ALLOWED_MAE = BASELINE_MAE * 1.20


def main() -> None:
    mlflow.set_tracking_uri(TRACKING_URI)

    results = pd.read_csv(RESULT_FILE)

    best_result = (
        results.sort_values(
            "rmse",
            ascending=True,
        )
        .iloc[0]
    )

    run_id = best_result["run_id"]
    run_name = best_result["run_name"]
    mae = float(best_result["mae"])
    rmse = float(best_result["rmse"])
    r2 = float(best_result["r2"])

    print("========================================")
    print("AUTOMATED MODEL EVALUATION")
    print("========================================")
    print(f"Best run       : {run_name}")
    print(f"Run ID         : {run_id}")
    print(f"MAE            : {mae:.4f}")
    print(f"RMSE           : {rmse:.4f}")
    print(f"R2             : {r2:.4f}")
    print(f"Maximum MAE    : {MAX_ALLOWED_MAE:.4f}")

    if mae > MAX_ALLOWED_MAE:
        print()
        print("VALIDATION RESULT: FAILED")
        print(
            "Model tidak memenuhi threshold performa. "
            "Registry tidak diperbarui."
        )
        sys.exit(1)

    print()
    print("VALIDATION RESULT: PASSED")

    model_uri = f"runs:/{run_id}/model"

    print()
    print("Registering validated model...")
    print("Model URI:", model_uri)

    registered_model = mlflow.register_model(
        model_uri=model_uri,
        name=REGISTERED_MODEL_NAME,
    )

    version = registered_model.version

    client = MlflowClient(
        tracking_uri=TRACKING_URI,
    )

    client.transition_model_version_stage(
        name=REGISTERED_MODEL_NAME,
        version=version,
        stage="Staging",
        archive_existing_versions=False,
    )

    print()
    print("========================================")
    print("AUTO-REGISTRY UPDATE SUCCESS")
    print("========================================")
    print(
        f"Registered model : {REGISTERED_MODEL_NAME}"
    )
    print(
        f"Version          : {version}"
    )
    print(
        "Stage            : Staging"
    )


if __name__ == "__main__":
    main()