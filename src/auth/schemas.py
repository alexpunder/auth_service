from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expire: datetime
    refresh_token_expire: datetime
    token_type: str


class UserCreate(BaseModel):
    phone_number: str
    password: str


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    phone_number: str


class UserRegistration(BaseModel):
    user: UserInDB
    token: TokenInfo
