import jwt
from fastapi.security import OAuth2PasswordBearer
from app.models import User,TokenPayload
from sqlmodel import Session
from app.core.db import engine
from collections.abc import Generator
from fastapi import Depends, HTTPException, status
from typing import Annotated
from app.core.config import SECRET_KEY
from app.core.security import ALGORITHM
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/access-token")   #template多了 /api/v1

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user(token: TokenDep, session: SessionDep) -> User :
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data  = TokenPayload(**payload)
    except (ValidationError, InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user

CurrentDep = Annotated[User, Depends(get_current_user)]

def get_current_active_superuser(user: CurrentDep) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user is no superuser",
        )
    return user
