import logging
import os
import time
import uuid

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import upload, search, clusters, documents, subjects, jobs, auth
from app.core.logging_config import setup_logging

# --------------------------------------------------
# Logging Setup
# --------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="AI Document Organizer",
    description="Local-first document intelligence platform",
    version="1.0.0",
)

# --------------------------------------------------
# Startup / Shutdown Events
# --------------------------------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown complete")


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "service": "U-MEM",
        "description": "Universal Memory Management System",
        "status": "running"
    }


# --------------------------------------------------
# Request ID + Logging Middleware
# --------------------------------------------------
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(
            "Unhandled exception before response | request_id=%s | path=%s",
            request_id,
            request.url.path,
        )
        raise exc

    duration = time.time() - start_time

    logger.info(
        "Request | id=%s | method=%s | path=%s | status=%s | duration=%.4fs",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    response.headers["X-Request-ID"] = request_id
    return response


# --------------------------------------------------
# CORS Configuration
# --------------------------------------------------
cors_origins_env = os.getenv("CORS_ORIGINS", "*")

if cors_origins_env == "*":
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    allow_credentials = True

logger.info("CORS configured | origins=%s", allow_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Global Exception Handler
# --------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    request_id = getattr(request.state, "request_id", "unknown")

    if isinstance(exc, HTTPException):
        logger.warning(
            "HTTPException | id=%s | path=%s | detail=%s",
            request_id,
            request.url.path,
            exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "request_id": request_id,
            },
        )

    logger.error(
        "Unhandled exception | id=%s | path=%s",
        request_id,
        request.url.path,
    )
    logger.exception(exc)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "request_id": request_id,
        },
    )


# --------------------------------------------------
# Health Endpoints
# --------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-document-organizer",
        "environment": os.getenv("ENV", "development"),
    }


@app.get("/health/storage")
def storage_health():
    try:
        from app.storage.metadata import load_chunks
        from app.storage.vector_store import index, metadata

        chunks = load_chunks()

        return {
            "status": "ok",
            "chunks_loaded": len(chunks),
            "vector_count": index.ntotal,
            "vector_metadata_count": len(metadata),
            "index_metadata_match": index.ntotal == len(metadata),
        }

    except Exception as e:
        logger.exception("Storage health check failed")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
            },
        )


# --------------------------------------------------
# API Versioning
# --------------------------------------------------
API_V1_PREFIX = "/api/v1"

app.include_router(upload.router, prefix=API_V1_PREFIX)
app.include_router(search.router, prefix=API_V1_PREFIX)
app.include_router(clusters.router, prefix=API_V1_PREFIX)
app.include_router(documents.router, prefix=API_V1_PREFIX)
app.include_router(subjects.router, prefix=API_V1_PREFIX)
app.include_router(jobs.router, prefix=API_V1_PREFIX)
app.include_router(auth.router, prefix=API_V1_PREFIX)
