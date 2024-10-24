from typing import Annotated

from fastapi import APIRouter, Depends, Form, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.auth.models import AuthenticatedUser
from src.auth.schemas import (
    TokenInfo,
    UserCreate,
    UserInDB,
)
from src.auth.service import auth_service
from src.auth.validations import auth_validator
from src.database import get_async_session

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
    hashed_pwd = auth_service.hash_password(registration_data.password)

    await auth_validator.check_user_phone_shoud_not_exist(
        session,
        registration_data.phone_number,
    )

    db_user = AuthenticatedUser(
        phone_number=registration_data.phone_number,
        hashed_password=hashed_pwd,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    jwt_token = auth_service.create_access_token(
        data={
            'user_id': db_user.id,
            'phone_number': db_user.phone_number,
        }
    )

    return TokenInfo(
        access_token=jwt_token,
        token_type='Bearer',
    )


async def validate_auth_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthenticatedUser:
    user = await auth_validator.check_user_phone_shoud_exist(
        session=session,
        user_phone=username,
    )
    auth_service.verified_password(
        input_password=password,
        hashed_password=user.hashed_password,
    )
    auth_validator.check_user_status(
        user=user,
    )
    return user


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=TokenInfo,
)
async def login_user(
    user: Annotated[UserCreate, Depends(validate_auth_user)],
):
    jwt_token = auth_service.create_access_token(
        data={
            'user_id': user.id,
            'phone_number': user.phone_number
        },
    )

    return TokenInfo(
        access_token=jwt_token,
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
