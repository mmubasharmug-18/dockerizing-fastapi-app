from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.config import load_settings
from app.handlers import validation_error_handler
from app.logs import setup_logging
from app.routes import health, vitals

settings = load_settings()
logger = setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Patient Vitals API (environment=%s, log level=%s)", settings.app_env, settings.log_level)
    yield
    logger.info("Patient Vitals API stopped")


app = FastAPI(
    title="Patient Vitals API",
    version="1.1.0",
    description=(
        "Receives, validates, stores and summarizes patient vitals. "
        f"Data is kept in memory. Environment: {settings.app_env}."
    ),
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_error_handler)

app.include_router(health.router)
app.include_router(vitals.router)
