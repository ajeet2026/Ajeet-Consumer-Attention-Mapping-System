from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.store import Store
from app.schemas.store_schema import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
)
from app.dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.post("/", response_model=StoreResponse)
def create_store(
    store: StoreCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    new_store = Store(
        name=store.name,
        location=store.location,
        manager_name=store.manager_name,
    )

    db.add(new_store)
    db.commit()
    db.refresh(new_store)

    return new_store


@router.get("/", response_model=list[StoreResponse])
def get_stores(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Store).all()


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return store


@router.put("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: int,
    data: StoreUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    store.name = data.name
    store.location = data.location
    store.manager_name = data.manager_name

    db.commit()
    db.refresh(store)

    return store


@router.delete("/{store_id}")
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    store = db.query(Store).filter(Store.id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    db.delete(store)
    db.commit()

    return {"message": "Store deleted successfully"}