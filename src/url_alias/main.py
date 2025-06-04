from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from url_alias.api.v1.api import api_router
from url_alias.api.v1.public import router as public_router
from url_alias.shared.logging import get_logger
from url_alias.shared.rate_limiting import limiter

logger = get_logger(__name__)

app = FastAPI(
    title="URL Alias Service",
    description="Сервис преобразования длинных URL в короткие уникальные URL",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api/v1")
app.include_router(public_router, tags=["public"])


@app.get("/")
def read_root():
    logger.info("Health check endpoint called")
    return {"message": "URL Alias Service is running"}


@app.on_event("startup")
async def startup_event():
    logger.info("URL Alias Service is starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("URL Alias Service is shutting down...")
