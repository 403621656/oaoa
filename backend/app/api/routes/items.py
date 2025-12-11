
from fastapi import HTTPException, Query, APIRouter
from app.models import DBItem, Item, ItemPublic, ItemsPublic
from typing import Annotated
from sqlmodel import select, func
from app.api.deps import SessionDep, CurrentDep
import uuid

router = APIRouter(
    prefix = "/items",
    tags = ["Items"],
)


@router.post("/", response_model=ItemPublic)
async def create_item(session: SessionDep,  user: CurrentDep, item: Item):
    db_item = DBItem.model_validate(item, update={"owner_id": user.id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def delete_item(item_id: uuid.UUID, user: CurrentDep, session: SessionDep):
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

@router.put("/{item_id}", response_model=ItemPublic)
async def update_item(item_id: uuid.UUID, item: Item, user: CurrentDep, session: SessionDep):
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

@router.get("/", response_model=ItemsPublic)
async def read_items(
    session: SessionDep,
    user: CurrentDep,
    offset: int = 0,
    limit: Annotated[int, Query(le = 100)] = 100,
):
    if user.is_superuser:
        statement = select(func.count()).select_from(DBItem)
        count = session.exec(statement).one()
        db_items = session.exec(select(DBItem).offset(offset).limit(limit)).all()
    else:
        statement = select(func.count).select_from(DBItem).where(DBItem.owner_id == user.id)
        count = session.exec(statement).one()
        db_items = session.exec(select(DBItem).offset(offset).limit(limit).where(DBItem.owner_id==user.id)).all()
    return ItemsPublic(data=db_items, count=count)

@router.get("/{item_id}", response_model=ItemPublic)
async def read_item(session: SessionDep,  user: CurrentDep, item_id: uuid.UUID):
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