import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.models import AuthenticatedUser
from src.auth.schemas import (
    UserCreate,
    UserInDB,
    Token,
)
from src.auth.service import auth_service
from src.auth.validations import auth_validator

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/registration',
    status_code=status.HTTP_201_CREATED,
    response_model=UserInDB,
)
async def user_registry(
    registration_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    logging.info(f'Поступившая информация: {registration_data.model_dump()}')

    hashed_pwd = auth_service.hash_password(registration_data.password)

    logging.info(f'Захешированный пароль: {hashed_pwd=}')

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

    return db_user


@router.post(
    '/login',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=Token,
)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    logging.info(
        'Введены следующие данные логин/пароль: '
        f'{login_data.username=}, {login_data.password=}'
    )

    user = await auth_validator.check_user_phone_shoud_exist(
        session=session,
        user_phone=login_data.username,
    )

    logging.info(
        f'Объект пользователя из БД: {user=}'
    )
    logging.info(
        'Пробуем вывести пароль пользователя из БД: '
        f'{user.hashed_password=}'
    )

    auth_service.verified_password(
        input_password=login_data.password,
        hashed_password=user.hashed_password,
    )
    jwt_token = auth_service.create_access_token(
        data={
            'user_id': user.id,
            'phone_number': user.phone_number
        }
    )

    logging.info(f'Вывод JWT-токена: {jwt_token=}')

    decoded_jwt_token = auth_service.decode_access_token(
        token=jwt_token,
    )

    logging.info(f'Вывод декодированного JWT-токена: {decoded_jwt_token=}')

    return Token(
        access_token=jwt_token,
        token_type='bearer',
    )


@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    await session.execute(
        delete(AuthenticatedUser)
        .where(AuthenticatedUser.id == user_id)
    )
    await session.commit()
