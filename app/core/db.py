from sqlmodel import create_engine, SQLModel, Session, select
from app.core.config import db_config
from app.models import User, UserCreate
import os
from dotenv import load_dotenv
from app.crud import create_user


load_dotenv()


sql_url = db_config.DATABASE_URL
engine = create_engine(sql_url)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def init_db(session:Session) -> None:
    statement = select(User).where(User.email==os.getenv("EMAIL"))
    user_super = session.exec(statement).first()
    if not user_super:
        create_super = UserCreate(
            username=os.getenv("USERNAME"),
            email=os.getenv("EMAIL"),
            password=os.getenv("PASSWORD"),
            is_superuser=True,
        )
        user_super = create_user(user_create=create_super, session=session)


