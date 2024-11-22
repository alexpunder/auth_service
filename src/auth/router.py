from typing import Annotated
from random import randint

from httpx import AsyncClient
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validations import validate_auth_user, auth_validator
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.auth.schemas import (
    PhoneInput,
    CodeInput,
    TokenInfo,
    UserInDB,
)
from src.auth.service import auth_service, producer
from src.auth.models import TokenType
from src.database import get_async_session
from src.config import settings

http_bearer = HTTPBearer()

router = APIRouter(
    prefix='/auth',
    # dependencies=[Depends(http_bearer)],
)

REDIS_STORAGE = {}


@router.post(
    '/send-registration-request',
    tags=['Покупатель']
)
async def buyer_registration_request(
    input_number: PhoneInput,
):
    verifier_code = str(randint(1000, 9999))
    # тут логика отправки сообщения пользователю на указанный номер

    REDIS_STORAGE[input_number.phone_number] = verifier_code

    print(f'Проверочный код: {verifier_code=}')

    async with AsyncClient(
        auth=(
            settings.auth_settings.SMS_LOGIN,
            settings.auth_settings.SMS_API_KEY,
        ),
    ) as client:
        response = await client.get(
            url=settings.auth_settings.SMS_BASE_URL + "auth",
        )
        SMS_PARAMS = {
            "number": input_number.phone_number,
            "text": verifier_code,
            "sign": "SMS Aero",
        }
        send_verifier_message = await client.get(
            url=settings.auth_settings.SMS_BASE_URL + "sms/send",
            params=SMS_PARAMS,
        )
        print(send_verifier_message.json())

    # логика добавления кода в Redis с проверкой делеем времени и отслеживанием количества попыток

    return 'Сообщение отправлено на указанный номер.'


@router.post(
    '/confirm-verifier-code',
    tags=['Покупатель'],
)
async def confirm_verifier_code(
    auth_data: CodeInput,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    print(f'Вывожу имитацию хранилица Redis: {REDIS_STORAGE=}')
    # получаем данные из Redis по номеру телефона
    verifier_code_in_memory = REDIS_STORAGE.get(auth_data.phone_number)

    if auth_data.code != verifier_code_in_memory:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Введенный пароль не соответствует отправленному.',
        )

    return 'Введен корректный пароль. Добро пожаловать!'


# @router.post(
#     '/registration',
#     status_code=status.HTTP_201_CREATED,
#     response_model=TokenInfo,
# )
# async def user_registration(
#     registration_data: UserCreate,
#     session: Annotated[AsyncSession, Depends(get_async_session)],
# ):
#     await auth_validator.check_user_phone_shoud_not_exist(
#         session,
#         registration_data.phone_number,
#     )

#     hashed_pwd = auth_service.hash_password(registration_data.password)

#     db_user = User(
#         phone_number=registration_data.phone_number,
#         hashed_password=hashed_pwd,
#     )

#     session.add(db_user)
#     await session.commit()
#     await session.refresh(db_user)

#     await producer.send_and_wait(
#         topic=settings.kafka_settings.TOPIC_NAME,
#         value=(
#             registration_data
#             .model_dump_json(include=('phone_number'))
#             .encode('utf-8')
#         )
#     )
#     user_data = {
#         'user_id': str(db_user.id),
#         'phone_number': db_user.phone_number,
#         'role': db_user.role,
#         'status': db_user.status,
#     }

#     access_expire, jwt_access_token = auth_service.create_token(
#         token_type=TokenType.ACCESS,
#         data=user_data,
#     )

#     refresh_expire, jwt_refresh_token = auth_service.create_token(
#         token_type=TokenType.REFRESH,
#         data=user_data,
#     )

#     return TokenInfo(
#         access_token=jwt_access_token,
#         refresh_token=jwt_refresh_token,
#         access_token_expire=access_expire,
#         refresh_token_expire=refresh_expire,
#         token_type='Bearer',
#     )


# @router.post(
#     '/login',
#     status_code=status.HTTP_200_OK,
#     response_model=TokenInfo,
# )
# async def login_user(
#     user: Annotated[AuthenticatedUser, Depends(validate_auth_user)],
# ):
#     user_data = {
#         'user_id': str(user.id),
#         'phone_number': user.phone_number,
#         'role': user.role,
#         'status': user.status,
#     }

#     access_expire, jwt_access_token = auth_service.create_token(
#         token_type=TokenType.ACCESS,
#         data=user_data,
#     )

#     refresh_expire, jwt_refresh_token = auth_service.create_token(
#         token_type=TokenType.REFRESH,
#         data=user_data,
#     )

#     return TokenInfo(
#         access_token=jwt_access_token,
#         refresh_token=jwt_refresh_token,
#         access_token_expire=access_expire,
#         refresh_token_expire=refresh_expire,
#         token_type='Bearer',
#     )


# @router.post(
#     '/refresh-token',
#     response_model=TokenInfo,
#     response_model_exclude_none=True,
# )
# async def refresh_access_token(
#     refresh_token: str,
#     session: Annotated[AsyncSession, Depends(get_async_session)],
# ):
#     access_expire, access_token = await auth_service.refresh_access_token(
#         refresh_token=refresh_token,
#         session=session,
#     )
#     return TokenInfo(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         access_token_expire=access_expire,
#         token_type='Bearer',
#     )


# @router.get(
#     '/me',
#     status_code=status.HTTP_200_OK,
#     response_model=UserInDB,
# )
# async def get_user(
#     current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
# ):
#     return current_user
