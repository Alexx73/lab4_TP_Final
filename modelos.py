from sqlalchemy import Column, Integer, String, Date, Time, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from datetime import datetime, timedelta


# Crear la clase base para las tablas
Base = declarative_base()

# Modelo SQLAlchemy para una Cancha
class Cancha(Base):
    __tablename__ = 'canchas'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(20), nullable=False)
    techada = Column(Boolean, default=False)
    reservas = relationship("Reserva", back_populates="cancha")  # Relación con la tabla Reserva

# Modelo SQLAlchemy para una Reserva
class Reserva(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    duracion = Column(Integer, nullable=False)
    hora_fin = Column(Time, nullable=False)  # Nueva columna para almacenar hora_fin
    telefono = Column(String(15), nullable=False)
    nombre_contacto = Column(String(100), nullable=False)
    cancha_id = Column(Integer, ForeignKey('canchas.id'), nullable=False)
    cancha = relationship("Cancha", back_populates="reservas")  # Relación con la tabla Cancha

@hybrid_property
def hora_fin(self):
        """Calcula la hora de finalización sumando duración (convertida de horas a minutos menos 1) a la hora de inicio."""
        if self.hora and self.duracion:
            # Convertir duración en horas a minutos, restando 1 minuto
            duracion_minutos = (self.duracion * 60) - 1
            hora_fin = (datetime.combine(datetime.min, self.hora) + timedelta(minutes=duracion_minutos)).time()
            return hora_fin
        return None

# Modelo SQLAlchemy para una Cancha
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(20), nullable=False)
    telefono = Column(String(15), nullable=False)
    email = Column(String(30), nullable=False)


