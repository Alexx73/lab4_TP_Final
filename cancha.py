from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Time, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Crear la clase base para las tablas
Base = declarative_base()

    # Modelo SQLAlchemy para una Cancha
class Cancha(Base):
    __tablename__ = 'canchas'
    id = Column(Integer, primary_key=True, index=True)
    nombre= Column(String(20), nullable=False)
    techada= Column(Boolean, default=False)
    reservas = relationship("Reserva", back_populates="canchas")  # Relación con la tabla Reserva


    
    