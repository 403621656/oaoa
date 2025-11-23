from fastapi import APIRouter,HTTPException   #Query
from pydantic import EmailStr
from app.api.items import SessionDep
from app.models import User, UserCreate, UserUpdate
from sqlmodel import select
from pwdlib import PasswordHash
#from typing import Annotated

def get_hashed_password(password:EmailStr) -> str:
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password)
    return hashed_password

router = APIRouter(
    prefix = "/users/",
    tags = ["users"]
)

@router.post("/", response_model=User)
async def create_user(user_create:UserCreate, session:SessionDep):
    db_user = User.model_validate(
        user_create, update={"hashed_password", get_hashed_password(user_create.password)}
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# @router.get("/", response_model=list[User])
# async def get_users(
#         *, session:SessionDep, offset: int = 0, limit:Annotated[int, Query(le=100)]=100
# ):
#     db_users = session.exec(select(User).offset(offset).limit(limit)).all()
#     return db_users

@router.patch("/{user_id}", response_model=User)
async def update_user(*, user_in:UserUpdate, user_id:int, session:SessionDep):
    user_db = session.get(User, user_id)
    user_update = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_update:
        hashed_password = get_hashed_password(user_update["password"])
        extra_data["hashed_password"] = hashed_password
    user_db.sqlmodel_update(user_update, update=extra_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@router.get("/", response_model=User)
async def get_user(*, email:EmailStr, session:SessionDep):
    db_url = select(User).where(User.email==email)
    db_user = session.exec(db_url).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user