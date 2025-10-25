from fastapi import FastAPI
from core.db import create_db_and_tables
from routers import category_router, product_router

app = FastAPI(title="Sistema de Gestión de Tienda Online")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(category_router.router)
app.include_router(product_router.router)

@app.get("/")
def home():
    return {"mensaje": "Bienvenido al Sistema de Gestión de Tienda Online"}
