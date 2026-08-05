from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.product import Product
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)
from app.dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    new_product = Product(
        name=product.name,
        brand=product.brand,
        price=product.price,
        shelf_id=product.shelf_id,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/", response_model=list[ProductResponse])
def get_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Product).all()


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = data.name
    product.brand = data.brand
    product.price = data.price
    product.shelf_id = data.shelf_id
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
