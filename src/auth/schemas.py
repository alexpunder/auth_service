from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, UUID4


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expire: datetime
    refresh_token_expire: datetime | None = None
    token_type: str


class UserCreate(BaseModel):
    phone_number: str
    password: str


class UserInDB(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={UUID4: str},
    )

    id: UUID4
    created_at: datetime
    phone_number: str


class UserRegistration(BaseModel):
    user: UserInDB
    token: TokenInfo
