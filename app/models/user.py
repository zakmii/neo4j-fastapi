from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserInDBBase(UserBase):
    id: str  # Using username as ID in Redis for simplicity, or generate a UUID

    class Config:
        from_attributes = True  # Replaces orm_mode = True in Pydantic v2


class UserInDB(UserInDBBase):
    hashed_password: str


class UserPublic(UserInDBBase):
    # Model for data returned to the client (omits password)
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
