import logging
from pathlib import Path
from typing import Sequence, Type

from fastapi.middleware import Middleware
from fastapi.responses import ORJSONResponse, Response
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.middleware import middleware

BASE_DIR = Path(__file__).parent.parent


class ExtendBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8', extra='ignore'
    )


class AppSettings(ExtendBaseSettings):
    model_config = SettingsConfigDict(env_prefix='APP_')

    DEBUG: bool = True
    LOG_LEVEL: str = 'INFO'
    TITLE: str = 'Auth service'
    SUMMARY: str = ''
    DESCRIPTION: str | None = 'Microservice'
    VERSION: str = '0.0.1'
    DOCS_URL: str = '/'
    REDOC_URL: str = '/redoc'
    DEFAULT_RESPONSE_CLASS: Type[Response] = ORJSONResponse
    MIDDLEWARE: Sequence[Middleware] = middleware
    TERMS_OF_SERVICE: str | None = None
    CONTACT: dict = {}
    LICENSE_INFO: dict = {}


class AuthSettings(ExtendBaseSettings):
    model_config = SettingsConfigDict(env_prefix='AUTH_')

    PUBLIC_KEY_PATH: Path = BASE_DIR / 'keys' / 'public-key.pem'
    PRIVATE_KEY_PATH: Path = BASE_DIR / 'keys' / 'private-key.pem'
    SECRET_KEY: str | bytes
    ALGORITHM: str
    EXPIRE: int


class DBSettings(ExtendBaseSettings):
    model_config = SettingsConfigDict(env_prefix='DB_')

    DSN: str = 'sqlite+aiosqlite:///./auth.db'


class KafkaSettings(ExtendBaseSettings):
    BOOTSTRAP_SERVERS: str = 'localhost:9092'
    TOPIC_NAME: str = 'auth_topic'


class Settings(ExtendBaseSettings):
    app_settings: AppSettings = AppSettings()
    auth_settings: AuthSettings = AuthSettings()
    db_settings: DBSettings = DBSettings()
    kafka_settings: KafkaSettings = KafkaSettings()


settings: Settings = Settings()
