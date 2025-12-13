from app.api.routes import items, users, login
from fastapi import APIRouter

router = APIRouter()

router.include_router(items.router)
router.include_router(users.router)
router.include_router(login.router)