import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import status
from fastapi.exceptions import HTTPException

from src.config import settings

loop = asyncio.get_event_loop()

producer = AIOKafkaProducer(
    loop=loop,
    bootstrap_servers=settings.kafka_settings.BOOTSTRAP_SERVERS,
)

consumer = AIOKafkaConsumer(
    settings.kafka_settings.TOPIC_NAME,
    loop=loop,
    bootstrap_servers=settings.kafka_settings.BOOTSTRAP_SERVERS,
)


class AuthService:
    def __init__(self):
        self.private_key: str = (
            settings.auth_settings.PRIVATE_KEY_PATH.read_text()
        )
        self.public_key: str = (
            settings.auth_settings.PUBLIC_KEY_PATH.read_text()
        )
        self.secret_key: str = settings.auth_settings.SECRET_KEY
        self.algorithm: str = settings.auth_settings.ALGORITHM
        self.expire: int = settings.auth_settings.EXPIRE_MINUTES

    def create_access_token(self, data: dict[str, Any]):
        to_encode = data.copy()
        now = datetime.now(tz=UTC)
        expire = now + timedelta(minutes=self.expire)
        to_encode.update(
            exp=expire,
            iat=now,
        )
        return jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str | bytes):
        return jwt.decode(
            jwt=token,
            key=self.public_key,
            algorithms=[self.algorithm],
        )

    @staticmethod
    def hash_password(password: str):
        bytes_pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password=bytes_pwd, salt=salt)

    @staticmethod
    def verified_password(input_password: str, hashed_password: bytes):
        if not bcrypt.checkpw(
            password=input_password.encode('utf-8'),
            hashed_password=hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка проверки логина или пароля.',
            )


auth_service = AuthService()
