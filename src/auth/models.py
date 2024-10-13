from datetime import datetime

from sqlalchemy import func, MetaData
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.constants import DB_NAMING_CONVENTION

metadata = MetaData(
    naming_convention=DB_NAMING_CONVENTION,
)


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
