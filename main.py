from fastapi import FastAPI
from core.db import init_db
from routers import category_router, product_router

app = FastAPI(title="Sistema de Gestión de Tienda Online")

app.include_router(category_router.router)
app.include_router(product_router.router)

@app.on_event("startup")
def on_startup():
    init_db()
