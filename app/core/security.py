import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from app.core.config import SECRET_KEY
import uuid


ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()

def get_hashed_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: uuid.UUID | str, expires_delta: timedelta):
    exp = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(data), "exp": exp}          #确保是str
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt