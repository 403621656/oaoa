from fastapi import HTTPException
from pydantic import EmailStr
from app.models import User, UserCreate, UserUpdate
from sqlmodel import select, Session
from app.core.security import get_hashed_password, verify_password



def get_user_by_email(*, email:EmailStr, session:Session):
    statement = select(User).where(User.email==email)
    db_user = session.exec(statement).first()
    return db_user

def authenticate(*, email:EmailStr, password:str, session:Session):
    db_user = get_user_by_email(email=email, session=session)
    if not db_user:
        raise HTTPException(status_code=404, detail="Incorrect email")
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=404, detail="Incorrect password")
    return db_user



def create_user(*, user_create:UserCreate, session:Session):
    db_user = User.model_validate(
        user_create, update={"hashed_password":get_hashed_password(user_create.password)}
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def update_user(*, user_in:UserUpdate, db_user:User, session:Session):
    user_update = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_update and user_update["password"]:
        hashed_password = get_hashed_password(user_update["password"])
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_update, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def get_user(*, email:EmailStr, session:Session):
    db_url = select(User).where(User.email==email)
    db_user = session.exec(db_url).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user