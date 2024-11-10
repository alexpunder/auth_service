import asyncio
from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import bcrypt
import jwt
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from fastapi import status
from fastapi.exceptions import HTTPException

from src.config import settings
from src.auth.models import TokenType

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


async def test_kafka_get_messages():
    logging.info('Начало цикла по выводу сообщений из очереди.')

    async for message in consumer:
        logging.info(f'Вывод сообщения полученного от Продюсера: {message=}')


class AuthService:
    def __init__(self):
        self.private_key: str = settings.auth_settings.get_private_key
        self.public_key: str = settings.auth_settings.get_public_key
        self.secret_key: str = settings.auth_settings.SECRET_KEY
        self.algorithm: str = settings.auth_settings.ALGORITHM
        self.access_expire: int = settings.auth_settings.ACCESS_EXPIRE_MINUTES
        self.refresh_expire: int = settings.auth_settings.REFRESH_EXPIRE_DAYS

    def create_token(self, token_type, data: dict[str, Any]) -> tuple[datetime, str]:
        to_encode = data.copy()
        now = datetime.now(tz=UTC)
        if type == TokenType.ACCESS:
            expire = now + timedelta(minutes=self.access_expire)
        else:
            expire = now + timedelta(days=self.refresh_expire)
        to_encode.update(
            token_type=token_type,
            exp=expire,
            iat=now,
        )
        return expire, jwt.encode(
            payload=to_encode,
            key=self.private_key,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str | bytes) -> dict[str, Any]:
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
