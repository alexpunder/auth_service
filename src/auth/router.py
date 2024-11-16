from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.validations import validate_auth_user, auth_validator
from src.auth.dependencies import get_current_user
from src.auth.models import AuthenticatedUser
from src.auth.schemas import (
    TokenInfo,
    UserCreate,
    UserInDB,
)
from src.auth.service import auth_service, producer
from src.auth.models import TokenType
from src.database import get_async_session
from src.config import settings

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    dependencies=[Depends(http_bearer)],
)


@router.post(
    '/registration',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenInfo,
)
async def user_registration(
    registration_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    await auth_validator.check_user_phone_shoud_not_exist(
        session,
        registration_data.phone_number,
    )

    hashed_pwd = auth_service.hash_password(registration_data.password)

    db_user = AuthenticatedUser(
        phone_number=registration_data.phone_number,
        hashed_password=hashed_pwd,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    await producer.send_and_wait(
        topic=settings.kafka_settings.TOPIC_NAME,
        value=(
            registration_data
            .model_dump_json(include=('phone_number'))
            .encode('utf-8')
        )
    )
    user_data = {
        'user_id': str(db_user.id),
        'phone_number': db_user.phone_number,
        'role': db_user.role,
        'status': db_user.status,
    }

    access_expire, jwt_access_token = auth_service.create_token(
        token_type=TokenType.ACCESS,
        data=user_data,
    )

    refresh_expire, jwt_refresh_token = auth_service.create_token(
        token_type=TokenType.REFRESH,
        data=user_data,
    )

    return TokenInfo(
        access_token=jwt_access_token,
        refresh_token=jwt_refresh_token,
        access_token_expire=access_expire,
        refresh_token_expire=refresh_expire,
        token_type='Bearer',
    )


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
)
async def login_user(
    user: Annotated[AuthenticatedUser, Depends(validate_auth_user)],
):
    user_data = {
        'user_id': str(user.id),
        'phone_number': user.phone_number,
        'role': user.role,
        'status': user.status,
    }

    access_expire, jwt_access_token = auth_service.create_token(
        token_type=TokenType.ACCESS,
        data=user_data,
    )

    refresh_expire, jwt_refresh_token = auth_service.create_token(
        token_type=TokenType.REFRESH,
        data=user_data,
    )

    return TokenInfo(
        access_token=jwt_access_token,
        refresh_token=jwt_refresh_token,
        access_token_expire=access_expire,
        refresh_token_expire=refresh_expire,
        token_type='Bearer',
    )


@router.post(
    '/refresh-token',
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
async def refresh_access_token(
    refresh_token: str,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    access_expire, access_token = await auth_service.refresh_access_token(
        refresh_token=refresh_token,
        session=session,
    )
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expire=access_expire,
        token_type='Bearer',
    )


@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=UserInDB,
)
async def get_user(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
):
    return current_user
