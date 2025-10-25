from fastapi import FastAPI, HTTPException, status, Query
from sqlmodel import Session
from database import init_db
import crud
from models import Category, Product
from typing import Optional

app = FastAPI(
    title="Tienda Online API",
    version="1.0",
    description="API para gestionar categorías y productos de una tienda online."
)


# =========================
# 🔹 EVENTO DE INICIO
# =========================
@app.on_event("startup")
def on_startup():
    """Crea las tablas de la base de datos al iniciar la app."""
    init_db()


# =========================
# 🟢 ENDPOINTS CATEGORÍAS
# =========================

@app.post("/categories/", status_code=status.HTTP_201_CREATED)
def create_category(payload: dict):
    """
    Crear categoría.
    - Valida nombre único.
    - Retorna 201 si se crea correctamente.
    """
    cat = Category(**payload)
    return crud.create_category(cat)


@app.get("/categories/")
def list_categories(active: bool = True):
    """
    Listar categorías.
    - Parámetro ?active=true muestra solo activas.
    """
    return crud.list_categories(active_only=active)


@app.get("/categories/{category_id}")
def get_category(category_id: int):
    """
    Obtener categoría por ID (incluye productos asociados).
    """
    cat = crud.get_category(category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@app.put("/categories/{category_id}")
def update_category(category_id: int, payload: dict):
    """
    Actualizar categoría.
    - Valida nombre único al renombrar.
    """
    return crud.update_category(category_id, payload)


@app.delete("/categories/{category_id}")
def delete_category(category_id: int):
    """
    Eliminar categoría (borrado en cascada).
    - Elimina también todos los productos asociados.
    """
    return crud.delete_category_cascade(category_id)


# =========================
# 🟣 ENDPOINTS PRODUCTOS
# =========================

@app.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(payload: dict):
    """
    Crear producto.
    - Debe pertenecer a una categoría existente.
    """
    prod = Product(**payload)
    return crud.create_product(prod)


@app.get("/products/")
def list_products(
    category_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    min_stock: Optional[int] = Query(None, ge=0, description="Stock mínimo"),
    max_price: Optional[float] = Query(None, gt=0, description="Precio máximo"),
    active: Optional[bool] = Query(None, description="Solo activos/inactivos")
):
    """
    Listar productos con filtros opcionales:
    - category_id, min_stock, max_price, active
    """
    filters = {
        "category_id": category_id,
        "min_stock": min_stock,
        "max_price": max_price,
        "active": active,
    }
    return crud.list_products(filters)


@app.get("/products/{product_id}")
def get_product(product_id: int):
    """
    Obtener producto por ID (incluye categoría).
    """
    prod = crud.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@app.put("/products/{product_id}")
def update_product(product_id: int, payload: dict):
    """
    Actualizar producto.
    - Valida que stock no sea negativo.
    - Valida que la categoría exista si se cambia.
    """
    return crud.update_product(product_id, payload)


@app.post("/products/{product_id}/deactivate")
def deactivate_product(product_id: int):
    """
    Desactivar producto (soft delete).
    """
    return crud.deactivate_product(product_id)


@app.post("/products/{product_id}/reduce_stock")
def reduce_stock(product_id: int, amount: int):
    """
    Reducir stock (simula una compra).
    - Valida que no quede negativo.
    """
    return crud.reduce_stock(product_id, amount)
