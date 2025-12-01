from sqlmodel import create_engine, SQLModel
from app.core.config import db_config


sql_url = db_config.DATABASE_URL
engine = create_engine(sql_url)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)