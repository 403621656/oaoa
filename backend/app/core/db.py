from sqlmodel import create_engine, SQLModel, Session, select
from app.core.config import settings
from app.models import User, UserCreate
from app.crud import create_user

sql_url = str(settings.SQLALCHEMY_DATABASE_URI)
engine = create_engine(sql_url)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def init_db(session:Session) -> None:
    statement = select(User).where(User.email==settings.FIRST_SUPERUSER)
    user_super = session.exec(statement).first()
    if not user_super:
        create_super = UserCreate(
            full_name=settings.FIRST_SUPERUSER_NAME,
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user_super = create_user(user_create=create_super, session=session)


