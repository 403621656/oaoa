from fastapi import Depends, HTTPException, Query, APIRouter
from ..models import DBItem, Item, get_session
from typing import Annotated
from sqlmodel import Session, select


router = APIRouter(
    prefix = "/items",
    tags = ["Items"],
    responses={404: {"description": "Not found"}}
)

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/")
async def create_items(item:Item, session:SessionDep):
    db_item = DBItem.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def delete_item(item_id:int, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found"
        )
    session.delete(db_item)
    session.commit()
    return {"OK" : "delete success"}

@router.patch("/{item_id}")
async def update_item(item_id:int, item:Item, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found"
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
    offset:int = 0,
    limit:Annotated[int, Query(le = 100)] = 100,
):
    db_items = session.exec(select(DBItem).offset(offset).limit(limit)).all()
    return db_items

@router.get("/{item_id}")
async def read_item(item_id:int, session:SessionDep):
    db_item = session.get(DBItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code = 404,
            detail = "not found"
        )
    return db_item