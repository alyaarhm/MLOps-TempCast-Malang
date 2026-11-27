"""Monitored MLflow model serving for LK-11."""

import socket
import time
from contextlib import asynccontextmanager

import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    Gauge,
    generate_latest,
)

MODEL_PATH = "/opt/ml/model"
REPLICA_ID = socket.gethostname()

model = None

REQUESTS = Counter(
    "tempcast_model_requests_total",
    "Total inference requests per model replica",
    ["replica", "status"],
)

LATENCY = Histogram(
    "tempcast_model_latency_seconds",
    "Model inference latency in seconds",
    ["replica"],
    buckets=(
        0.001, 0.005, 0.01, 0.025,
        0.05, 0.1, 0.25, 0.5,
        1.0, 2.5, 5.0,
    ),
)

ERRORS = Counter(
    "tempcast_model_errors_total",
    "Total inference errors",
    ["replica"],
)

PREDICTIONS = Histogram(
    "tempcast_model_prediction",
    "Distribution of predicted temperatures",
    ["replica"],
    buckets=(
        15, 20, 22, 24, 26, 28,
        30, 32, 34, 36, 38, 40, 45,
    ),
)

LATEST_PREDICTION = Gauge(
    "tempcast_model_latest_prediction",
    "Latest predicted temperature",
    ["replica"],
)

MODEL_READY = Gauge(
    "tempcast_model_ready",
    "Model readiness status",
    ["replica"],
)

REQUESTS.labels(REPLICA_ID, "success")
REQUESTS.labels(REPLICA_ID, "error")
ERRORS.labels(REPLICA_ID)
LATENCY.labels(REPLICA_ID)
PREDICTIONS.labels(REPLICA_ID)
MODEL_READY.labels(REPLICA_ID).set(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model

    model = mlflow.pyfunc.load_model(MODEL_PATH)

    MODEL_READY.labels(REPLICA_ID).set(1)

    print(f"Model loaded successfully: {REPLICA_ID}")

    yield

    MODEL_READY.labels(REPLICA_ID).set(0)


app = FastAPI(
    title="TempCast Monitored Model",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
@app.get("/ping")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "replica": REPLICA_ID,
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/invocations")
def invocations(payload: dict):
    start_time = time.perf_counter()

    try:
        if model is None:
            raise HTTPException(
                status_code=503,
                detail="Model is not ready",
            )

        records = payload.get("dataframe_records")

        if not records:
            raise HTTPException(
                status_code=400,
                detail="dataframe_records is required",
            )

        dataframe = pd.DataFrame(records)

        predictions = model.predict(dataframe)

        results = [
            float(value)
            for value in predictions
        ]

        for prediction in results:
            PREDICTIONS.labels(
                REPLICA_ID
            ).observe(prediction)

            LATEST_PREDICTION.labels(
                REPLICA_ID
            ).set(prediction)

        REQUESTS.labels(
            REPLICA_ID,
            "success",
        ).inc()

        return {
            "predictions": results,
            "replica": REPLICA_ID,
        }

    except HTTPException:
        ERRORS.labels(REPLICA_ID).inc()

        REQUESTS.labels(
            REPLICA_ID,
            "error",
        ).inc()

        raise

    except Exception as error:
        ERRORS.labels(REPLICA_ID).inc()

        REQUESTS.labels(
            REPLICA_ID,
            "error",
        ).inc()

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:
        LATENCY.labels(
            REPLICA_ID
        ).observe(
            time.perf_counter() - start_time
        )