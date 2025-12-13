from fastapi import FastAPI
import uvicorn
from app.core.db import create_db_and_tables, init_db, engine
from app.api import main
from contextlib import asynccontextmanager
from sqlmodel import Session
from app.core.db import engine
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        init_db(session)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main.router, prefix="/api/v1")



if __name__ ==   "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
