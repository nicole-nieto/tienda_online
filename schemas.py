from sqlmodel import SQLModel
from typing import Optional, List
from models import ProductBase, CategoryBase


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    # productos incluidos en la respuesta
    products: Optional[List["ProductRead"]]


class CategoryUpdate(SQLModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]


class ProductCreate(ProductBase):
    category_id: int


class ProductRead(ProductBase):
    id: int
    category_id: int


class ProductUpdate(SQLModel):
    name: Optional[str]
    price: Optional[float]
    stock: Optional[int]
    description: Optional[str]
    active: Optional[bool]
    category_id: Optional[int]