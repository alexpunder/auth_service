from datetime import datetime
from enum import StrEnum

from sqlalchemy import MetaData, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.constants import DB_NAMING_CONVENTION

metadata = MetaData(
    naming_convention=DB_NAMING_CONVENTION,
)


class UserRole(StrEnum):
    SUPERUSER = 'администратор'
    REGULAR_USER = 'обычный пользователь'


class UserStatus(StrEnum):
    IS_BLOCKED = 'заблокирован'
    IS_ACTIVE = 'активный'


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    metadata = metadata

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )


class AuthenticatedUser(Base):
    __tablename__ = 'authenticated_users'

    phone_number: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(
        default=UserRole.REGULAR_USER,
    )
    status: Mapped[UserStatus] = mapped_column(
        default=UserStatus.IS_ACTIVE,
    )
