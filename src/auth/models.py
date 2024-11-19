from uuid import UUID, uuid4
from datetime import datetime
from enum import StrEnum

from sqlalchemy import MetaData, func, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.constants import DB_NAMING_CONVENTION

metadata = MetaData(
    naming_convention=DB_NAMING_CONVENTION,
)


class TokenType(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class UserType(StrEnum):
    SELLER = 'seller'
    BUYER = 'buyer'


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    metadata = metadata

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )


class User(Base):
    __tablename__ = 'users'

    phone_number: Mapped[str]
    type: Mapped[UserType]
    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

    refresh_token: Mapped[list["RefreshToken"]] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
    )


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    token: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
    )
    fingerprint: Mapped[str] = mapped_column(
        unique=True,
    )
    revoked: Mapped[bool] = mapped_column(
        default=False,
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user: Mapped['User'] = relationship(
        back_populates='refresh_tokens',
    )
