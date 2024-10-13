import jwt
import asyncio
from datetime import datetime, timedelta, UTC

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import bcrypt
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
        self.secret_key = settings.auth_settings.SECRET_KEY
        self.algorithm = settings.auth_settings.ALGORITHM
        self.expire = settings.auth_settings.EXPIRE

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(tz=UTC) + timedelta(minutes=self.expire)
        to_encode.update({'exp': expire})
        return jwt.encode(
            payload=to_encode,
            key=self.secret_key,
            algorithm=self.algorithm,
        )

    def decode_access_token(self, token: str | bytes):
        return jwt.decode(
            jwt=token,
            key=self.secret_key,
            algorithms=self.algorithm,
        )

    @staticmethod
    def hash_password(password: str):
        bytes_pwd = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(
            password=bytes_pwd, salt=salt
        )

    @staticmethod
    def verified_password(input_password: str, hashed_password: bytes):
        if not bcrypt.checkpw(
            password=input_password.encode('utf-8'),
            hashed_password=hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка проверки пароля: не совпадает!'
            )


auth_service = AuthService()
