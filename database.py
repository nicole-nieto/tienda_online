from sqlmodel import create_engine, SQLModel
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")


# Para SQLite: connect_args required
engine = create_engine(DATABASE_URL, echo=False)


def init_db():
SQLModel.metadata.create_all(engine)