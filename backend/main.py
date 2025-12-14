from fastapi import FastAPI
import uvicorn
from app.core.db import create_db_and_tables, init_db, engine
from app.api import main
from contextlib import asynccontextmanager
from sqlmodel import Session
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        init_db(session)
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(main.router, prefix=settings.API_V1_STR)



if __name__ ==   "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
