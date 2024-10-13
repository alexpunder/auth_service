from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import AuthenticatedUser


class AuthValidation:
    def __init__(self, model):
        self.model = model

    async def check_user_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> AuthenticatedUser | None:
        user_exists = await session.execute(
            select(self.model)
            .where(self.model.phone_number == user_phone)
        )

        return user_exists.scalar_one_or_none()

    async def check_user_phone_shoud_not_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> AuthenticatedUser | None:
        if (user_object := await self.check_user_exist(
            session=session,
            user_phone=user_phone,
        )):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Пользователь с таким номером телефона уже существует.'
            )

        return user_object

    async def check_user_phone_shoud_exist(
        self,
        session: AsyncSession,
        user_phone: str,
    ) -> AuthenticatedUser | None:
        if not (user_object := await self.check_user_exist(
            session=session,
            user_phone=user_phone,
        )):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Пользователь с таким номером не найден.'
            )

        return user_object


auth_validator = AuthValidation(AuthenticatedUser)
