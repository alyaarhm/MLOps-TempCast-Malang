"""TempCast Malang inference API with Prometheus observability for LK-11."""

import os
import time
from contextlib import asynccontextmanager

import mlflow
import mlflow.sklearn
import numpy as np
import requests
from fastapi import FastAPI, HTTPException, Response
from mlflow.tracking import MlflowClient
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
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

# Drift dinyatakan sebagai perubahan mean relatif terhadap baseline training.
# Threshold 0.15 berarti perubahan mean >= 15% dianggap sebagai indikasi drift.
DRIFT_THRESHOLD = 0.15

model = None
model_version = None

baseline_feature_means = {}
feature_sums = {}
feature_counts = {}


# ============================================================
# PROMETHEUS METRICS
# ============================================================

INFERENCE_REQUESTS = Counter(
    "tempcast_inference_requests_total",
    "Total number of inference requests.",
    ["status"],
)

INFERENCE_ERRORS = Counter(
    "tempcast_inference_errors_total",
    "Total number of inference errors.",
)

INFERENCE_LATENCY = Histogram(
    "tempcast_inference_latency_seconds",
    "Inference request latency in seconds.",
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ),
)

PREDICTION_VALUE = Gauge(
    "tempcast_prediction_value",
    "Latest predicted maximum temperature.",
)

PREDICTION_DISTRIBUTION = Histogram(
    "tempcast_prediction_distribution",
    "Distribution of predicted maximum temperature.",
    buckets=(
        15,
        20,
        22,
        24,
        26,
        28,
        30,
        32,
        34,
        36,
        38,
        40,
        45,
    ),
)

FEATURE_BASELINE_MEAN = Gauge(
    "tempcast_feature_baseline_mean",
    "Baseline mean of each input feature from training data.",
    ["feature"],
)

FEATURE_CURRENT_MEAN = Gauge(
    "tempcast_feature_current_mean",
    "Running mean of each feature received by the API.",
    ["feature"],
)

FEATURE_DRIFT_SCORE = Gauge(
    "tempcast_feature_drift_score",
    "Relative mean shift between current input and training baseline.",
    ["feature"],
)

FEATURE_DRIFT_DETECTED = Gauge(
    "tempcast_feature_drift_detected",
    "Drift indicator: 1 when drift score exceeds threshold, otherwise 0.",
    ["feature"],
)

DRIFT_THRESHOLD_METRIC = Gauge(
    "tempcast_drift_threshold",
    "Configured drift detection threshold.",
)

DRIFT_THRESHOLD_METRIC.set(DRIFT_THRESHOLD)


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


def initialize_drift_baseline() -> None:
    """Create baseline means from the training portion of the dataset."""
    global baseline_feature_means
    global feature_sums
    global feature_counts

    try:
        dataframe = load_and_prepare_data()

        (
            x_train,
            _,
            _,
            _,
        ) = chronological_split(
            dataframe
        )

        baseline_feature_means = {
            feature: float(x_train[feature].mean())
            for feature in FEATURE_COLUMNS
            if feature in x_train.columns
        }

        for feature, mean_value in baseline_feature_means.items():
            FEATURE_BASELINE_MEAN.labels(
                feature=feature
            ).set(mean_value)

            FEATURE_CURRENT_MEAN.labels(
                feature=feature
            ).set(mean_value)

            FEATURE_DRIFT_SCORE.labels(
                feature=feature
            ).set(0)

            FEATURE_DRIFT_DETECTED.labels(
                feature=feature
            ).set(0)

            feature_sums[feature] = 0.0
            feature_counts[feature] = 0

        print(
            "Drift baseline initialized from training data."
        )

    except Exception as error:
        print(
            f"Warning: drift baseline initialization failed: {error}"
        )


def update_drift_metrics(feature_values: dict) -> None:
    """Update running feature means and simple mean-shift drift metrics."""
    for feature, value in feature_values.items():
        if feature not in baseline_feature_means:
            continue

        numeric_value = float(value)

        feature_sums[feature] += numeric_value
        feature_counts[feature] += 1

        current_mean = (
            feature_sums[feature]
            / feature_counts[feature]
        )

        baseline_mean = baseline_feature_means[feature]

        denominator = max(
            abs(baseline_mean),
            1e-6,
        )

        drift_score = abs(
            current_mean - baseline_mean
        ) / denominator

        drift_detected = (
            1
            if drift_score >= DRIFT_THRESHOLD
            else 0
        )

        FEATURE_CURRENT_MEAN.labels(
            feature=feature
        ).set(current_mean)

        FEATURE_DRIFT_SCORE.labels(
            feature=feature
        ).set(drift_score)

        FEATURE_DRIFT_DETECTED.labels(
            feature=feature
        ).set(drift_detected)


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

    initialize_drift_baseline()

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
    version="1.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {
        "service": "TempCast Malang API",
        "status": "running",
        "observability": "Prometheus metrics enabled",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
    }


@app.get("/metrics")
def metrics():
    """Expose Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


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
        "drift_threshold": DRIFT_THRESHOLD,
    }


@app.post("/predict")
def predict(payload: PredictionInput):
    start_time = time.perf_counter()

    try:
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Model is not loaded.",
            )

        feature_values = {
            "temperature_2m_min":
                payload.temperature_2m_min,
            "temperature_2m_mean":
                payload.temperature_2m_mean,
            "precipitation_sum":
                payload.precipitation_sum,
            "wind_speed_10m_max":
                payload.wind_speed_10m_max,
            "temperature_2m_max_lag1":
                payload.temperature_2m_max_lag1,
            "temperature_2m_max_lag3":
                payload.temperature_2m_max_lag3,
            "temperature_2m_max_lag7":
                payload.temperature_2m_max_lag7,
            "temperature_2m_max_roll3_mean":
                payload.temperature_2m_max_roll3_mean,
            "temperature_2m_max_roll7_mean":
                payload.temperature_2m_max_roll7_mean,
            "month":
                payload.month,
            "day_of_year":
                payload.day_of_year,
        }

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

        prediction = float(
            model.predict(row)[0]
        )

        update_drift_metrics(
            feature_values
        )

        PREDICTION_VALUE.set(
            prediction
        )

        PREDICTION_DISTRIBUTION.observe(
            prediction
        )

        INFERENCE_REQUESTS.labels(
            status="success"
        ).inc()

        return {
            "predicted_temperature_max": round(
                prediction,
                4,
            ),
            "model_name": MODEL_NAME,
            "model_version": model_version,
        }

    except HTTPException:
        INFERENCE_ERRORS.inc()

        INFERENCE_REQUESTS.labels(
            status="error"
        ).inc()

        raise

    except Exception as error:
        INFERENCE_ERRORS.inc()

        INFERENCE_REQUESTS.labels(
            status="error"
        ).inc()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:
        elapsed = (
            time.perf_counter()
            - start_time
        )

        INFERENCE_LATENCY.observe(
            elapsed
        )