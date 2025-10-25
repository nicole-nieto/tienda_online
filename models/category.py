from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.product import Product

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str

    products: List["Product"] = Relationship(back_populates="category")
