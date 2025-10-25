from sqlmodel import SQLModel, Field, Relationship, ForeignKey
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    price: float
    stock: int = Field(ge=0)
    active: bool = Field(default=True)
    category_id: int = Field(foreign_key="category.id")

    category: Optional["Category"] = Relationship(back_populates="products")
