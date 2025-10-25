from sqlmodel import Session, select
from database import engine
from models import Category, Product
from fastapi import HTTPException
from typing import List, Optional

# =======================
# 🟢 CATEGORY CRUD
# =======================

def create_category(category: Category) -> Category:
    """Crea una categoría (nombre único)."""
    with Session(engine) as session:
        # Validar unicidad
        statement = select(Category).where(Category.name == category.name)
        existing = session.exec(statement).first()
        if existing:
            raise HTTPException(status_code=409, detail="Category with this name already exists")

        session.add(category)
        session.commit()
        session.refresh(category)
        return category


def list_categories(active_only: bool = True) -> List[Category]:
    """Lista todas las categorías (solo activas si active_only=True)."""
    with Session(engine) as session:
        statement = select(Category)
        if active_only:
            statement = statement.where(Category.active == True)
        return session.exec(statement).all()


def get_category(category_id: int) -> Optional[Category]:
    """Obtiene una categoría por su ID, incluyendo productos."""
    with Session(engine) as session:
        cat = session.get(Category, category_id)
        return cat


def update_category(category_id: int, data: dict) -> Category:
    """Actualiza los datos de una categoría (valida nombre único)."""
    with Session(engine) as session:
        cat = session.get(Category, category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        # Si se cambia el nombre, verificar que no exista otro igual
        if "name" in data and data["name"] != cat.name:
            q = select(Category).where(Category.name == data["name"])
            existing = session.exec(q).first()
            if existing:
                raise HTTPException(status_code=409, detail="Category with this name already exists")

        for key, value in data.items():
            setattr(cat, key, value)

        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat


def delete_category_cascade(category_id: int):
    """Elimina la categoría y sus productos asociados (borrado en cascada)."""
    with Session(engine) as session:
        cat = session.get(Category, category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

        # Eliminar productos asociados antes de borrar la categoría
        products = session.exec(select(Product).where(Product.category_id == category_id)).all()
        for p in products:
            session.delete(p)

        session.delete(cat)
        session.commit()
        return {"deleted_category": category_id, "deleted_products": len(products)}


# =======================
# 🟣 PRODUCT CRUD
# =======================

def create_product(product: Product) -> Product:
    """Crea un producto (requiere categoría existente)."""
    with Session(engine) as session:
        cat = session.get(Category, product.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category does not exist")

        session.add(product)
        session.commit()
        session.refresh(product)
        return product


def list_products(filters: dict) -> List[Product]:
    """Lista productos con filtros opcionales (categoría, stock, precio, activo)."""
    with Session(engine) as session:
        statement = select(Product)

        if "category_id" in filters and filters["category_id"] is not None:
            statement = statement.where(Product.category_id == filters["category_id"])
        if "min_stock" in filters and filters["min_stock"] is not None:
            statement = statement.where(Product.stock >= filters["min_stock"])
        if "max_price" in filters and filters["max_price"] is not None:
            statement = statement.where(Product.price <= filters["max_price"])
        if "active" in filters and filters["active"] is not None:
            statement = statement.where(Product.active == filters["active"])

        return session.exec(statement).all()


def get_product(product_id: int) -> Optional[Product]:
    """Obtiene un producto por su ID."""
    with Session(engine) as session:
        return session.get(Product, product_id)


def update_product(product_id: int, data: dict) -> Product:
    """Actualiza un producto (valida stock y categoría existente)."""
    with Session(engine) as session:
        prod = session.get(Product, product_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found")

        if "stock" in data and data["stock"] < 0:
            raise HTTPException(status_code=400, detail="Stock cannot be negative")

        if "category_id" in data:
            cat = session.get(Category, data["category_id"])
            if not cat:
                raise HTTPException(status_code=404, detail="New category not found")

        for key, value in data.items():
            setattr(prod, key, value)

        session.add(prod)
        session.commit()
        session.refresh(prod)
        return prod


def deactivate_product(product_id: int) -> Product:
    """Desactiva un producto (soft delete)."""
    with Session(engine) as session:
        prod = session.get(Product, product_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found")

        prod.active = False
        session.add(prod)
        session.commit()
        session.refresh(prod)
        return prod


def reduce_stock(product_id: int, amount: int) -> Product:
    """Reduce el stock de un producto al comprarlo (sin permitir negativos)."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    with Session(engine) as session:
        prod = session.get(Product, product_id)
        if not prod:
            raise HTTPException(status_code=404, detail="Product not found")

        if prod.stock - amount < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        prod.stock -= amount
        session.add(prod)
        session.commit()
        session.refresh(prod)
        return prod
