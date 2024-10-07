from fastapi import FastAPI

from src.auth import auth_router
from src.config import settings

app = FastAPI(
    debug=settings.app_settings.debug,
    title=settings.app_settings.title,
    summary=settings.app_settings.summary,
    description=settings.app_settings.description,
    version=settings.app_settings.version,
    docs_url=settings.app_settings.docs_url,
    redoc_url=settings.app_settings.redoc_url,
    default_response_class=settings.app_settings.default_response_class,
    middleware=settings.app_settings.middleware,
    terms_of_service=settings.app_settings.terms_of_service,
    contact=settings.app_settings.contact,
    license_info=settings.app_settings.license_info,
)

app.include_router(
    router=auth_router,
)
