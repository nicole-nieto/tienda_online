from pydantic import BaseModel, Field
from typing import Optional
from schemas.category_schema import CategoryReadSimple  # 👈 usa el modelo simple

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int = Field(ge=0)
    category_id: int

class ProductRead(ProductCreate):
    id: int
    active: bool
    category: Optional[CategoryReadSimple] = None  # 👈 modelo liviano

    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    stock: Optional[int] = Field(ge=0)
    active: Optional[bool]
