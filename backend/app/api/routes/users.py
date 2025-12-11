from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import CurrentDep, SessionDep, get_current_active_superuser
from app import crud
from app.models import User, UserCreate, UserRegister, UserUpdate, UserUpdateMe, DBItem, UserPublic, UsersPublic
from sqlmodel import select, delete, col
from typing import Annotated
import uuid

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=UsersPublic)
async def get_users(
        session:SessionDep,
        offset:int=0,
        limit:Annotated[int, Query(le=100)] = 100,
):

    statement = select(User).offset(offset).limit(limit)
    users = session.exec(statement).all()
    return UsersPublic(data=users, count=777)

@router.get("/me", response_model=UserPublic)
async def get_user(current_user:CurrentDep):
    return current_user

@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def create_user(*, session:SessionDep, user_in:UserCreate):
    user_db = crud.get_user_by_email(email=user_in.email, session=session)
    if user_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_db = crud.create_user(user_create=user_in, session=session)
    return user_db

@router.post("/signup", response_model=UserPublic)
async def register_user(session:SessionDep, user_in:UserRegister):
    user_db = crud.get_user_by_email(email=user_in.email, session=session)
    if user_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_create = UserCreate.model_validate(user_in)
    user_db = crud.create_user(user_create=user_create, session=session)
    return user_db

@router.delete("/me")
async def delete_me(session: SessionDep, current_user: CurrentDep):
    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")
    statement = delete(DBItem).where(DBItem.owner_id==current_user.id)
    session.exec(statement)
    session.delete(current_user)
    session.commit()
    return {"message": "User deleted successfully"}

@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)],response_model=UserPublic)
async def delete_user(session: SessionDep, current_user: CurrentDep, user_id: uuid.UUID):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    if user_db == current_user:
        raise HTTPException(status_code=403, detail="Super users are not allowed to delete themselves")
    statement = delete(DBItem).where(col(DBItem.owner_id)==user_id)
    session.exec(statement)
    session.delete(user_db)
    session.commit()
    return {"message": "User deleted successfully"}

@router.patch("/me", response_model=UserPublic)
async def update_me(*, session:SessionDep, current_user:CurrentDep, user_in:UserUpdateMe):
    if user_in.email:
        user_new = crud.get_user_by_email(email=user_in.email, session=session)
        if user_new and user_new.email != current_user.email:
            raise HTTPException(status_code=409, detail="Email already registered")
    user_update = UserUpdate.model_validate(user_in)
    user = crud.update_user(session=session, db_user=current_user, user_in=user_update)
    return user

@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def update_user(*, session:SessionDep, user_id:uuid.UUID, user_in:UserUpdate):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    if user_in.email:
        user_new = crud.get_user_by_email(email=user_in.email, session=session)
        if user_new and user_id != user_new.id:
            raise HTTPException(status_code=409, detail="Email already registered")
    user_db = crud.update_user(session=session, db_user=user_db, user_in=user_in)
    return user_db

