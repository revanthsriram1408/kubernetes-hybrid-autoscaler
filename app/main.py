import os

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="Hybrid Autoscaler Demo", version="1.0.0")
WORK_ITERATIONS = int(os.getenv("WORK_ITERATIONS", "3000000"))
REQUEST_COUNT = Counter("demo_requests_total", "Total requests", ["endpoint"])
REQUEST_LATENCY = Histogram("demo_request_latency_seconds", "Request latency", ["endpoint"])


@app.get("/")
def root():
    REQUEST_COUNT.labels(endpoint="/").inc()
    return {"message": "Hybrid autoscaler demo app is running"}


@app.get("/work")
def work():
    REQUEST_COUNT.labels(endpoint="/work").inc()
    with REQUEST_LATENCY.labels(endpoint="/work").time():
        total = sum(i * i for i in range(WORK_ITERATIONS))
    return {"status": "ok", "checksum": total % 1_000_003}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
