from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    stock: int
    description: str
    active: bool = True
    category_id: int = Field(foreign_key="category.id")

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    products: List["Product"] = Relationship(back_populates="category", sa_relationship_kwargs={"cascade": "all, delete"})

Product.category = Relationship(back_populates="products")
