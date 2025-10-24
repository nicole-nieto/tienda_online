from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.category import Category, Product

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(product: Product, session: Session = Depends(get_session)):
    category = session.get(Category, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if product.stock < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.get("/")
def list_products(category_id: int = None, min_price: float = None, session: Session = Depends(get_session)):
    query = select(Product)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if min_price:
        query = query.where(Product.price >= min_price)
    return session.exec(query).all()

@router.put("/{product_id}")
def update_product(product_id: int, updated: Product, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for attr, value in updated.dict(exclude_unset=True).items():
        setattr(product, attr, value)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.patch("/{product_id}/deactivate")
def deactivate_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.active = False
    session.add(product)
    session.commit()
    return {"message": "Product deactivated"}

@router.patch("/{product_id}/buy/{quantity}")
def buy_product(product_id: int, quantity: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock - quantity < 0:
        raise HTTPException(status_code=400, detail="Not enough stock")
    product.stock -= quantity
    session.add(product)
    session.commit()
    return {"message": f"Purchased {quantity} units", "remaining_stock": product.stock}
