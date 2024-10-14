from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    phone_number: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str
    hashed_password: str
