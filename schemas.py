from pydantic import BaseModel
from datetime import date, time
from typing import Optional


# Pydantic model para validar los datos de entrada
class CanchaCreate(BaseModel):
    nombre: str
    techada: bool

class CanchaUpdate(BaseModel):
    nombre: str
    techada: bool
    
# Esquema de entrada para crear una reserva
class ReservaCreate(BaseModel):
    dia: str  # Fecha en formato "YYYY-MM-DD"
    hora: str  # Hora en formato "HH:MM:SS"
    duracion: int  # Duración en minutos
    telefono: str
    nombre_contacto: str
    cancha_id: int

class ReservaResponse(BaseModel):
    id: int
    dia: date
    hora: time
    duracion: int
    hora_fin: time
    telefono: str
    nombre_contacto: str
    cancha_id: int

    class Config:
        orm_mode = True  # Habilita la conversión de objetos ORM a Pydantic
 # -------------------   
# class CanchaBase(BaseModel):
#     nombre: str
#     techada: bool

# class CanchaCreate(CanchaBase):
#     pass

# class Cancha(CanchaBase):
#     id: int

#     class Config:
#         orm_mode = True

# class ReservaBase(BaseModel):
#     dia: datetime
#     duracion: int
#     telefono: str
#     nombre_contacto: str
#     cancha_id: int

# class ReservaCreate(ReservaBase):
#     pass

# class Reserva(ReservaBase):
#     id: int

#     class Config:
#         orm_mode = True
