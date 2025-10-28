from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.product import Product  # solo para hints, no ejecuta

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str
    active: bool = Field(default=True)  # 👈 NUEVO

    products: List["Product"] = Relationship(back_populates="category")

from models.product import Product  # noqa: E402, F401
