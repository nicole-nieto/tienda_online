#Tienda Online - Backend (FastAPI + SQLModel)
Descripción general

Este proyecto implementa el backend de una tienda en línea desarrollada con FastAPI y SQLModel.
El sistema permite la gestión de categorías y productos, incluyendo su activación, desactivación y relaciones entre ellos.

El objetivo es ofrecer una arquitectura limpia, modular y escalable basada en principios RESTful, con integración a una base de datos relacional.

⚙️ Tecnologías utilizadas

🐍 Python 3.11+

⚡ FastAPI (framework principal)

🗃️ SQLModel (ORM basado en SQLAlchemy + Pydantic)

🛢️ SQLite / PostgreSQL (según configuración)

🧩 Uvicorn (servidor ASGI)

🔐 Pydantic (validación de datos)

🧠 Dependencias inyectadas (DI) de FastAPI


Estructura

tienda_online/
│
├── core/
│   ├── config.py           # Configuración global (DATABASE_URL, etc.)
│   └── db.py               # Conexión a la base de datos y sesión
│
├── models/
│   ├── category.py         # Modelo Category (categorías)
│   └── product.py          # Modelo Product (productos)
│
├── routers/
│   ├── category_router.py  # Endpoints para categorías
│   └── product_router.py   # Endpoints para productos
│
├── schemas/
│   ├── category_schema.py  # Esquemas Pydantic para categorías
│   └── product_schema.py   # Esquemas Pydantic para productos
│
├── main.py                 # Punto de entrada principal de FastAPI
└── requirements.txt        # Dependencias del proyecto

# Instalación

```bash
pip install -r requirements.txt
