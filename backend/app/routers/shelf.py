from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.shelf import Shelf
from app.schemas.shelf_schema import (
    ShelfCreate,
    ShelfUpdate,
    ShelfResponse,
)
from app.dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/shelves", tags=["Shelves"])


@router.post("/", response_model=ShelfResponse)
def create_shelf(
    shelf: ShelfCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    new_shelf = Shelf(
        name=shelf.name,
        store_id=shelf.store_id,
    )
    db.add(new_shelf)
    db.commit()
    db.refresh(new_shelf)
    return new_shelf


@router.get("/", response_model=list[ShelfResponse])
def get_shelves(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Shelf).all()


@router.get("/{shelf_id}", response_model=ShelfResponse)
def get_shelf(
    shelf_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf


@router.put("/{shelf_id}", response_model=ShelfResponse)
def update_shelf(
    shelf_id: int,
    data: ShelfUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    shelf.name = data.name
    shelf.store_id = data.store_id
    db.commit()
    db.refresh(shelf)
    return shelf


@router.delete("/{shelf_id}")
def delete_shelf(
    shelf_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    db.delete(shelf)
    db.commit()
    return {"message": "Shelf deleted successfully"}
