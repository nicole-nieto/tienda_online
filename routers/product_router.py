from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.product import Product
from models.category import Category
from schemas.product_schema import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    category = session.get(Category, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    new_product = Product(**product.dict())
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product

@router.get("/", response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    return products

@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.delete("/{product_id}")
def deactivate_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.active = False
    session.add(product)
    session.commit()
    return {"message": "Product deactivated"}

@router.post("/{product_id}/buy")
def buy_product(product_id: int, quantity: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    product.stock -= quantity
    session.add(product)
    session.commit()
    return {"message": f"Purchased {quantity} units of {product.name}"}
