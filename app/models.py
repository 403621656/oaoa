from sqlmodel import Field, create_engine, SQLModel, Session, Relationship
from .config import db_config
from pydantic import EmailStr
import uuid


sql_url = db_config.DATABASE_URL
engine = create_engine(sql_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = True

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["DBItem"] = Relationship(back_populates="owner", cascade_delete=True)

class Item(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class DBItem(Item, table=True):
    id: int = Field(default=None, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")