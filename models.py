from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import validator


class ProductBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=120)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)
    active: bool = Field(default=True)

    @validator("name")
    def name_strip(cls, v):
        return v.strip()


class CategoryBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = Field(None, max_length=300)
    active: bool = Field(default=True)

    @validator("name")
    def name_strip(cls, v):
        return v.strip()


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # unique constraint emulado por verificación en CRUD
    products: List["Product"] = Relationship(back_populates="category")


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    category: Optional[Category] = Relationship(back_populates="products")