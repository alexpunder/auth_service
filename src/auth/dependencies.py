import logging
from typing import Annotated

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthenticatedUser
from src.auth.service import auth_service
from src.database import get_async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> AuthenticatedUser:
    logging.info('Проверяем токен пользователя')
    payload = auth_service.decode_access_token(
        token=token,
    )
    logging.info(f'Декодированный токен пользователя: {payload=}')
    user_id = payload.get('user_id')

    current_user_db = await session.execute(
        select(AuthenticatedUser).where(AuthenticatedUser.id == user_id)
    )

    current_user = current_user_db.scalar_one_or_none()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль.',
            headers={'WWW-Authenticate": "Bearer'},
        )

    return current_user
