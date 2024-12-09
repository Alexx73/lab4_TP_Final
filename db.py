from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:Pgre1508@localhost:5432/tpfinal"

# Crear el motor de base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear la clase base para las tablas
Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()