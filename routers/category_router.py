from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.category import Category
from models.product import Product
from schemas.category_schema import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])

# Crear categoría (único sin importar mayúsculas/minúsculas)
@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    # Buscar si ya existe una categoría con el mismo nombre (sin distinguir mayúsculas/minúsculas)
    existing_category = session.exec(
        select(Category).where(Category.name.ilike(category.name))
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"La categoría '{category.name}' ya existe."
        )

    # Si no existe, crear la nueva
    new_category = Category(
        name=category.name.strip(),
        description=category.description.strip()
    )

    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


# Listar solo categorías activas
@router.get("/", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category).where(Category.active == True)).all()
    return categories

# Consultar por ID
@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category

# Actualizar categoría
@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(category, key, value)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

# Desactivar categoría
@router.delete("/{category_id}")
def deactivate_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Desactivar la categoría
    category.active = False

    # Desactivar todos los productos relacionados
    products = session.exec(
        select(Product).where(Product.category_id == category.id)
    ).all()

    for product in products:
        product.active = False
        session.add(product)

    session.add(category)
    session.commit()

    return {
        "message": f"Categoría '{category.name}' y sus productos asociados fueron desactivados correctamente."
    }
