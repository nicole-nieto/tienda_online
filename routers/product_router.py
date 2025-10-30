from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from core.db import get_session
from models.product import Product
from models.category import Category
from schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from typing import Optional, List

router = APIRouter(prefix="/products", tags=["Products"])


#  Crear un nuevo producto
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    """
    Crea un nuevo producto, validando que la categoría exista.
    """
    category = session.get(Category, product.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Verificar que no exista otro producto con el mismo nombre en la misma categoría
    existing = session.exec(
        select(Product).where(Product.name.ilike(product.name), Product.category_id == product.category_id)
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un producto con el nombre '{product.name}' en esta categoría."
        )

    try:
        new_product = Product(**product.dict())
        session.add(new_product)
        session.commit()
        session.refresh(new_product)
        return new_product
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el producto: {e}")


#  Listar productos con filtros avanzados
@router.get("/", response_model=List[ProductRead])
def list_products(
    session: Session = Depends(get_session),
    name: Optional[str] = Query(None, description="Buscar por nombre (coincidencia parcial)"),
    category_id: Optional[int] = Query(None, description="Filtrar por id de categoría"),
    max_price: Optional[float] = Query(None, gt=0, description="Precio máximo"),
    min_stock: Optional[int] = Query(None, ge=0, description="Stock mínimo"),
    include_inactive: bool = Query(False, description="Incluir productos inactivos si es True"),
):
    """
    Lista productos filtrando por nombre, categoría, precio o stock.
    Por defecto, solo muestra productos activos.
    """
    try:
        conditions = []
        if not include_inactive:
            conditions.append(Product.active == True)

        if name:
            conditions.append(Product.name.ilike(f"%{name}%"))
        if category_id is not None:
            conditions.append(Product.category_id == category_id)
        if max_price is not None:
            conditions.append(Product.price <= max_price)
        if min_stock is not None:
            conditions.append(Product.stock >= min_stock)

        query = select(Product).where(*conditions) if conditions else select(Product)
        products = session.exec(query).all()

        if not products:
            raise HTTPException(status_code=404, detail="No se encontraron productos con los filtros aplicados.")

        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar productos: {e}")


#  Obtener un producto por ID
@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    """
    Devuelve un producto específico por su ID.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


#  Actualizar un producto
@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: int, data: ProductUpdate, session: Session = Depends(get_session)):
    """
    Actualiza los datos de un producto existente.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    try:
        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar el producto: {e}")


#  Desactivar un producto (borrado lógico)
@router.delete("/{product_id}")
def deactivate_product(product_id: int, session: Session = Depends(get_session)):
    """
    Desactiva (no elimina físicamente) un producto.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if not product.active:
        raise HTTPException(status_code=400, detail="El producto ya está inactivo")

    try:
        product.active = False
        session.add(product)
        session.commit()
        return {"message": f"Producto '{product.name}' desactivado correctamente."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al desactivar el producto: {e}")


#  Comprar producto
@router.post("/{product_id}/buy")
def buy_product(
    product_id: int,
    quantity: int = Query(..., gt=0, description="Cantidad a comprar"),
    session: Session = Depends(get_session),
):
    """
    Simula la compra de un producto, restando stock.
    """
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not product.active:
        raise HTTPException(status_code=400, detail="El producto está inactivo")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")

    try:
        product.stock -= quantity
        session.add(product)
        session.commit()
        return {"message": f"Compra exitosa: {quantity} unidades de '{product.name}'"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al procesar la compra: {e}")


#  Listar productos por categoría
@router.get("/category/{category_id}", response_model=List[ProductRead])
def get_products_by_category(category_id: int, session: Session = Depends(get_session)):
    """
    Muestra todos los productos activos asociados a una categoría específica.
    """
    products = session.exec(
        select(Product).where(Product.category_id == category_id, Product.active == True)
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No se encontraron productos para esta categoría")
    return products


#  Filtrar por estado (activos o inactivos)
@router.get("/status/", response_model=List[ProductRead])
def list_products_by_status(
    active: bool = Query(True, description="Filtrar productos activos (True) o inactivos (False)"),
    session: Session = Depends(get_session)
):
    """
    Lista productos según su estado (activos o inactivos).
    """
    products = session.exec(select(Product).where(Product.active == active)).all()

    if not products:
        estado = "activos" if active else "inactivos"
        raise HTTPException(status_code=404, detail=f"No se encontraron productos {estado}.")

    return products
