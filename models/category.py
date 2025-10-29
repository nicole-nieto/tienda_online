from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.product import Product

#Modelo que representa la tabla "category" en la base de datos
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str
    active: bool = Field(default=True)

    # Relación con los productos asociados a esta categoría
    products: List["Product"] = Relationship(back_populates="category")

from models.product import Product  
