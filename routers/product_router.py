from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from core.db import get_session
from models.product import Product
from models.category import Category
from schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from typing import Optional, List


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    category = session.get(Category, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    new_product = Product(**product.dict())
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.get("/", response_model=List[ProductRead])
def list_products(
    session: Session = Depends(get_session),
    name: Optional[str] = Query(None, description="Buscar por nombre (coincidencia parcial)"),
    category_id: Optional[int] = Query(None, description="Filtrar por id de categoría"),
    max_price: Optional[float] = Query(None, gt=0, description="Precio máximo"),
    min_stock: Optional[int] = Query(None, ge=0, description="Stock mínimo"),
    include_inactive: bool = Query(False, description="Incluir productos inactivos si es True"),
):
    # Construimos condiciones dinámicamente
    conditions = []
    if not include_inactive:
        conditions.append(Product.active == True)  # por defecto solo activos

    if name:
        # ilike para búsqueda case-insensitive y parcial
        conditions.append(Product.name.ilike(f"%{name}%"))

    if category_id is not None:
        conditions.append(Product.category_id == category_id)

    if max_price is not None:
        conditions.append(Product.price <= max_price)

    if min_stock is not None:
        conditions.append(Product.stock >= min_stock)

    # Si no hay condiciones, selecciona todo (pero normalmente habrá al menos active==True)
    if conditions:
        query = select(Product).where(*conditions)
    else:
        query = select(Product)

    products = session.exec(query).all()
    return products


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.get("/", response_model=list[ProductRead])
def list_products(
    session: Session = Depends(get_session),
    min_stock: Optional[int] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None
):
    query = select(Product).where(Product.active == True)

    if min_stock is not None:
        query = query.where(Product.stock >= min_stock)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if category_id is not None:
        query = query.where(Product.category_id == category_id)

    products = session.exec(query).all()
    return products



@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}")
def deactivate_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.active = False
    session.add(product)
    session.commit()
    return {"message": f"Producto '{product.name}' desactivado"}


@router.post("/{product_id}/buy")
def buy_product(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Cantidad a comprar"),
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not product.active:
        raise HTTPException(status_code=400, detail="El producto está inactivo")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")

    product.stock -= quantity
    session.add(product)
    session.commit()
    return {"message": f"Compra exitosa: {quantity} unidades de '{product.name}'"}

# En routers/products.py o routers/categories.py (como prefieras)
@router.get("/category/{category_id}", response_model=list[ProductRead])
def get_products_by_category(category_id: int, session: Session = Depends(get_session)):
    products = session.exec(select(Product).where(Product.category_id == category_id, Product.active == True)).all()
    if not products:
        raise HTTPException(status_code=404, detail="No se encontraron productos para esta categoría")
    return products
