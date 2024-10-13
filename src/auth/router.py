import logging
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.auth.models import AuthenticatedUser

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.get('/')
async def get_test_response():
    return {'status': 'ok'}


class UserCreate(BaseModel):
    phone_number: str
    password: str


class UserLogin(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    phone_number: str
    hashed_password: str


def hash_password(password: str):
    bytes_pwd = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(
        password=bytes_pwd, salt=salt
    )


def verified_password(input_password: str, hashed_password: bytes):
    if not bcrypt.checkpw(
        password=input_password.encode('utf-8'),
        hashed_password=hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка проверки пароля: не совпадает!'
        )


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

    hashed_pwd = hash_password(registration_data.password)

    logging.info(f'Захешированный пароль: {hashed_pwd=}')

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
    # response_model=Token,
)
async def login_user(
    login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    logging.info(
        'Введены следующие данные логин/пароль: '
        f'{login_data.username=}, {login_data.password=}'
    )

    user = await session.execute(
        select(AuthenticatedUser)
        .where(AuthenticatedUser.phone_number == login_data.username)
    )

    user_pwd = user.scalar_one_or_none()

    logging.info(
        f'Объект пользователя из БД: {user=}'
    )
    logging.info(
        'Пробуем вывести пароль пользователя из БД: '
        f'{user_pwd.hashed_password=}'
    )

    verified_password(
        input_password=login_data.password,
        hashed_password=user_pwd.hashed_password,
    )

    return {'status': 'ok'}


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
