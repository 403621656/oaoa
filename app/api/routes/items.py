
from fastapi import HTTPException, Query, APIRouter
from app.models import DBItem, Item
from typing import Annotated
from sqlmodel import select
from app.api.deps import SessionDep,CurrentDep

router = APIRouter(
    prefix = "/items",
    tags = ["Items"],
    responses={404: {"description": "Not found"}}
)


@router.post("/")
async def create_item(item:Item, user:CurrentDep, session:SessionDep):
    db_item = DBItem.model_validate(item, update={"owner_id":user.id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def delete_item(item_id:int, user:CurrentDep, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found",
        )
    if not user.is_superuser and db_item.owner_id != user.id:
        raise HTTPException(
            status_code = 400,
            detail = "Not enough permissions",
        )
    session.delete(db_item)
    session.commit()
    return {"message" : "deleted successfully"}

@router.patch("/{item_id}")
async def update_item(item_id:int, item:Item, user:CurrentDep, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found"
        )
    if not user.is_superuser and db_item.owner_id != user.id:
        raise HTTPException(
            status_code = 400,
            detail = "Not enough permissions",
        )
    db_new = item.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(db_new)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.get("/")
async def read_items(
    session:SessionDep,
    user:CurrentDep,
    offset:int = 0,
    limit:Annotated[int, Query(le = 100)] = 100,
):
    if user.is_superuser:
        db_items = session.exec(select(DBItem).offset(offset).limit(limit)).all()
    else:
        db_items = session.exec(select(DBItem).offset(offset).limit(limit).where(DBItem.owner_id==user.id)).all()
    return db_items

@router.get("/{item_id}")
async def read_item(item_id:int, user:CurrentDep, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found"
        )
    if not user.is_superuser and db_item.owner_id != user.id:
        raise HTTPException(
            status_code = 400,
            detail = "Not enough permissions",
        )
    return db_item