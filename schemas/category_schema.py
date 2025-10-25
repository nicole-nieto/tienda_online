from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    description: str

class CategoryRead(CategoryCreate):
    id: int

    class Config:
        orm_mode = True
