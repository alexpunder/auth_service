import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth import auth_router
from src.config import settings

LOG_LEVEL: str = settings.app_settings.LOG_LEVEL or 'INFO'

logging.basicConfig(
    format='%(asctime)s, %(name)s, %(levelname)s: %(message)s',
    level=LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass


app = FastAPI(
    debug=settings.app_settings.DEBUG,
    title=settings.app_settings.TITLE,
    summary=settings.app_settings.SUMMARY,
    description=settings.app_settings.DESCRIPTION,
    version=settings.app_settings.VERSION,
    docs_url=settings.app_settings.DOCS_URL,
    redoc_url=settings.app_settings.REDOC_URL,
    default_response_class=settings.app_settings.DEFAULT_RESPONSE_CLASS,
    middleware=settings.app_settings.MIDDLEWARE,
    terms_of_service=settings.app_settings.TERMS_OF_SERVICE,
    contact=settings.app_settings.CONTACT,
    license_info=settings.app_settings.LICENSE_INFO,
    # lifespan=lifespan,
)

app.include_router(
    router=auth_router,
)
