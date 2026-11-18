"""TempCast Malang inference API for LK-09 Docker Compose orchestration."""

import os
import time
from contextlib import asynccontextmanager

import mlflow
import mlflow.sklearn
import requests
from fastapi import FastAPI, HTTPException
from mlflow.tracking import MlflowClient
from pydantic import BaseModel
from sklearn.linear_model import LinearRegression

from src.train import (
    FEATURE_COLUMNS,
    chronological_split,
    evaluate_model,
    load_and_prepare_data,
)


MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-server:5000",
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "TempCast-Malang-LK09-Model",
)

EXPERIMENT_NAME = "TempCast-Malang-LK09"

model = None
model_version = None


class PredictionInput(BaseModel):
    temperature_2m_min: float
    temperature_2m_mean: float
    precipitation_sum: float
    wind_speed_10m_max: float
    temperature_2m_max_lag1: float
    temperature_2m_max_lag3: float
    temperature_2m_max_lag7: float
    temperature_2m_max_roll3_mean: float
    temperature_2m_max_roll7_mean: float
    month: int
    day_of_year: int


def wait_for_mlflow(max_attempts: int = 30) -> None:
    """Wait until MLflow server is reachable."""
    health_url = f"{MLFLOW_TRACKING_URI}/health"

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                health_url,
                timeout=3,
            )

            if response.status_code == 200:
                print(
                    f"MLflow available at {MLFLOW_TRACKING_URI}"
                )
                return

        except requests.RequestException:
            pass

        print(
            f"Waiting for MLflow... "
            f"attempt {attempt}/{max_attempts}"
        )

        time.sleep(2)

    raise RuntimeError(
        "MLflow server is not reachable."
    )


def get_latest_registered_version():
    """Return latest registered model version if available."""
    client = MlflowClient(
        tracking_uri=MLFLOW_TRACKING_URI,
    )

    try:
        versions = client.search_model_versions(
            f"name='{MODEL_NAME}'"
        )
    except Exception:
        return None

    if not versions:
        return None

    latest_version = max(
        versions,
        key=lambda item: int(item.version),
    )

    return str(latest_version.version)


def train_and_register_model():
    """Train model and register it to MLflow Registry."""
    mlflow.set_experiment(
        EXPERIMENT_NAME
    )

    dataframe = load_and_prepare_data()

    (
        x_train,
        x_test,
        y_train,
        y_test,
    ) = chronological_split(
        dataframe
    )

    candidate_model = LinearRegression()

    with mlflow.start_run(
        run_name="lk09_linear_regression"
    ):
        candidate_model.fit(
            x_train,
            y_train,
        )

        mae, rmse, r2 = evaluate_model(
            candidate_model,
            x_test,
            y_test,
        )

        mlflow.log_param(
            "model_type",
            "LinearRegression",
        )

        mlflow.log_param(
            "feature_count",
            len(FEATURE_COLUMNS),
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

        model_info = mlflow.sklearn.log_model(
            sk_model=candidate_model,
            name="model",
            serialization_format="cloudpickle",
        )

    registered_model = mlflow.register_model(
        model_uri=model_info.model_uri,
        name=MODEL_NAME,
    )

    return str(
        registered_model.version
    )


def prepare_model() -> None:
    """Load existing model or create one if registry is empty."""
    global model
    global model_version

    wait_for_mlflow()

    mlflow.set_tracking_uri(
        MLFLOW_TRACKING_URI
    )

    existing_version = (
        get_latest_registered_version()
    )

    if existing_version is not None:
        model_version = existing_version

        print(
            "Existing model found in MLflow Registry"
        )
        print(
            f"Using model version: {model_version}"
        )

    else:
        print(
            "No registered model found."
        )
        print(
            "Training and registering initial model..."
        )

        model_version = (
            train_and_register_model()
        )

    registry_uri = (
        f"models:/{MODEL_NAME}/{model_version}"
    )

    model = mlflow.sklearn.load_model(
        registry_uri
    )

    print(
        "Model successfully loaded from MLflow Registry"
    )
    print(
        f"Model name: {MODEL_NAME}"
    )
    print(
        f"Model version: {model_version}"
    )
    print(
        f"Model URI: {registry_uri}"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    prepare_model()
    yield


app = FastAPI(
    title="TempCast Malang API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "service": "TempCast Malang API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.get("/mlflow-check")
def mlflow_check():
    """Verify API-to-MLflow communication."""
    try:
        response = requests.get(
            f"{MLFLOW_TRACKING_URI}/health",
            timeout=5,
        )

        return {
            "mlflow_uri": MLFLOW_TRACKING_URI,
            "reachable": (
                response.status_code == 200
            ),
            "status_code": response.status_code,
        }

    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


@app.get("/model-info")
def model_info():
    return {
        "model_name": MODEL_NAME,
        "model_version": model_version,
        "loaded_from": "MLflow Model Registry",
        "tracking_uri": MLFLOW_TRACKING_URI,
    }


@app.post("/predict")
def predict(payload: PredictionInput):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    row = [[
        payload.temperature_2m_min,
        payload.temperature_2m_mean,
        payload.precipitation_sum,
        payload.wind_speed_10m_max,
        payload.temperature_2m_max_lag1,
        payload.temperature_2m_max_lag3,
        payload.temperature_2m_max_lag7,
        payload.temperature_2m_max_roll3_mean,
        payload.temperature_2m_max_roll7_mean,
        payload.month,
        payload.day_of_year,
    ]]

    prediction = model.predict(row)[0]

    return {
        "predicted_temperature_max": round(
            float(prediction),
            4,
        ),
        "model_name": MODEL_NAME,
        "model_version": model_version,
    }