from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Time, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship




# Crear la clase base para las tablas
Base = declarative_base()

# Modelo SQLAlchemy para la tabla "reservas"
class Reserva(Base):
    __tablename__ = 'reservas'

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracion = Column(Integer, nullable=False)
    telefono = Column(String(15), nullable=False)
    nombre_contacto = Column(String(100), nullable=False)
    cancha_id = Column(Integer, ForeignKey('canchas.id'), nullable=False)
    cancha = relationship("Cancha", back_populates="reservas")  # Relación con la tabla Cancha
    
    
    # cancha_id = Column(Integer, nullable=False)
    # cancha = relationship("Cancha", back_populates="reservas")