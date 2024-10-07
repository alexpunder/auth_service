from typing import Type, Sequence

from fastapi.middleware import Middleware
from fastapi.responses import ORJSONResponse, Response

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.middleware import middleware


class ExtendBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


class AppSettings(ExtendBaseSettings):
    model_config = SettingsConfigDict(env_prefix='APP_')

    debug: bool = True
    title: str = 'Auth service'
    summary: str = ''
    description: str | None = 'Microservice'
    version: str = '0.0.1'
    docs_url: str = '/'
    redoc_url: str = '/redoc'
    default_response_class: Type[Response] = ORJSONResponse
    middleware: Sequence[Middleware] = middleware
    terms_of_service: str | None = None
    contact: dict = {}
    license_info: dict = {}


class DBSettings(ExtendBaseSettings):
    model_config = SettingsConfigDict(env_prefix='DB_')

    dsn: str = 'sqlite+aiosqlite:///./auth.db'


class Settings(ExtendBaseSettings):
    app_settings: AppSettings = AppSettings()
    db_settings: DBSettings = DBSettings()


settings: Settings = Settings()
