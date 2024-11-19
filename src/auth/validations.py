from typing import Annotated
from fastapi import Depends, Form, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.service import auth_service
from src.database import get_async_session


class AuthValidation:
    def __init__(self, model):
        self.model = model

    async def check_user_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> User | None:
        user_exists = await session.execute(
            select(self.model).where(self.model.phone_number == user_phone)
        )

        return user_exists.scalar_one_or_none()

    async def check_user_phone_shoud_not_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> User | None:
        if user_object := await self.check_user_exist(
            session=session,
            user_phone=user_phone,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пользователь с таким номером телефона уже существует.',
            )

        return user_object

    async def check_user_phone_shoud_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> User | None:
        if not (
            user_object := await self.check_user_exist(
                session=session,
                user_phone=user_phone,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Ошибка проверки логина или пароля.',
            )

        return user_object

    def check_user_status(
        self,
        user: User,
    ):
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='К сожалению, Вы заблокированы.'
            )


auth_validator = AuthValidation(User)


async def validate_auth_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    user = await auth_validator.check_user_phone_shoud_exist(
        session=session,
        user_phone=username,
    )
    auth_validator.check_user_status(
        user=user,
    )
    return user
