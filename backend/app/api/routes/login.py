from app.crud import authenticate
from app.models import Token
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.api.deps import SessionDep
from app.core.config import ACESS_TOKEN_EXPIRE_MINUTES
from app.core.security import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(*, form_data : Annotated[OAuth2PasswordRequestForm, Depends()], session : SessionDep):
    user = authenticate(email=form_data.username, password=form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    expire = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=user.id, expires_delta=expire)
    return Token(access_token=access_token, token_type="bearer")


