from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    phone_number: str
    password: str


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str


class UserRegistration(BaseModel):
    user: UserInDB
    token: Token
