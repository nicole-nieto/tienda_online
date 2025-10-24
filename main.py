from fastapi import FastAPI
from core.db import init_db
from routers.category_router import router as category_router
from routers.product_router import router as product_router

app = FastAPI(title="Sistema de Gestión de Tienda Online")

# Incluir los routers
app.include_router(category_router)
app.include_router(product_router)

# Evento que inicializa la base de datos al iniciar la app
@app.on_event("startup")
def on_startup():
    init_db()