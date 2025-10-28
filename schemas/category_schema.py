from pydantic import BaseModel
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str
    description: str

class CategoryCreate(CategoryBase):
    pass

class CategoryReadSimple(BaseModel):  # 👈 Agrega esto
    id: int
    name: str

    class Config:
        from_attributes = True  # reemplaza orm_mode=True

class CategoryRead(CategoryBase):
    id: int
    active: bool

    class Config:
        from_attributes = True

class CategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    active: Optional[bool]
