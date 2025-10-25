from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from core.db import get_session
from models.category import Category
from schemas.category_schema import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = session.exec(select(Category).where(Category.name == category.name)).first()
    if db_category:
        raise HTTPException(status_code=409, detail="Category name must be unique")

    new_category = Category(**category.dict())
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category

@router.get("/", response_model=list[CategoryRead])
def list_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryCreate, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = data.name
    category.description = data.description
    session.add(category)
    session.commit()
    session.refresh(category)
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"message": "Category deleted successfully"}
