from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import time
import uuid

EMAIL = "YOUR_EMAIL@example.com"   # Replace with your exam email

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

# Keep last 1000 logs
logs = deque(maxlen=1000)

# Prometheus Counter
REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    REQUEST_COUNTER.inc()

    request_id = str(uuid.uuid4())

    entry = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id,
    }

    logs.append(entry)

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/work")
def work(n: int = 1):
    # simulate K units of work
    for _ in range(max(0, n)):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    limit = max(0, min(limit, 100))
    return list(logs)[-limit:]


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/")
def home():
    return {
        "status": "running"
    }
