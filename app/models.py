from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr, field_validator
import uuid
from datetime import datetime


def validate_username_format(v) -> str:
    if len(v)!=8:
        raise ValueError("Username must be in YYYYMMDD format")
    try:
        datetime.strptime(v, "%Y%m%d")
    except ValueError:
        raise ValueError("Username must be in YYYYMMDD format")
    return v



class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    username: str = Field(max_length=255)
    @field_validator("username")
    @classmethod
    def validate_username(cls, v:str) -> str:
        return validate_username_format(v)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=255)
    @field_validator("username")
    @classmethod
    def validate_username(cls, v:str) -> str:
        return validate_username_format(v)

class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    username: str | None = Field(default=None, max_length=255)
    @field_validator("username")
    @classmethod
    def validate_username(cls, v:str) -> str:
        return validate_username_format(v)

class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(max_length=255)
    @field_validator("username")
    @classmethod
    def validate_username(cls, v:str) -> str:
        return validate_username_format(v)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["DBItem"] = Relationship(back_populates="owner")

class Item(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class DBItem(Item, table=True):
    id: int = Field(default=None, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")

class TokenPayload(SQLModel):
    sub:str

class Token(SQLModel):
    access_token: str
    token_type: str