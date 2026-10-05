import sentry_sdk

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.database import engine, Base, init_db_schema
from app.services.storage_service import storage_service
from app.api import auth, document, privacy, clause, legal, analysis, chat, negotiation

# Setup Structured JSON Logging
setup_logging()

# Initialize Sentry Error Monitoring if DSN provided
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=1.0
    )

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_PER_MINUTE])

# Initialize Database tables & run schema auto-migration
init_db_schema()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Enterprise Legal AI SaaS Platform grounded in Indian Statutory Laws"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Register routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(document.router, prefix=settings.API_V1_STR)
app.include_router(privacy.router, prefix=settings.API_V1_STR)
app.include_router(clause.router, prefix=settings.API_V1_STR)
app.include_router(legal.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(negotiation.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["System"])
def health_check():
    db_healthy = False
    try:
        with engine.connect() as conn:
            conn.execute(Base.metadata.tables[list(Base.metadata.tables.keys())[0]].select().limit(1))
            db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "system": settings.PROJECT_NAME,
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "database": {
            "connected": db_healthy,
            "type": "PostgreSQL" if not settings.DATABASE_URL.startswith("sqlite") else "SQLite"
        },
        "storage": {
            "type": "AWS_S3" if storage_service.use_s3 else "LOCAL_ENCRYPTED_AES256",
            "encrypted": True
        },
        "error_monitoring": "Sentry Enabled" if settings.SENTRY_DSN else "Local Logging",
        "rate_limiting": f"Active ({settings.RATE_LIMIT_PER_MINUTE})"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
