from datetime import datetime

from pydantic import BaseModel, UUID4


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str
    access_token_expire: datetime
    refresh_token_expire: datetime | None = None
    token_type: str


class PhoneInput(BaseModel):
    phone_number: str


class VerifierCode(BaseModel):
    code: str


class CodeInput(BaseModel):
    phone_number: str
    code: str


class UserInDB(BaseModel):
    id: UUID4
    phone_number: str
    created_at: datetime


class UserRegistration(BaseModel):
    user: UserInDB
    token: TokenInfo
