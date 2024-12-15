from pydantic import BaseModel, field_validator
from datetime import date, time, datetime
from typing import Optional


# Pydantic model para validar los datos de entrada
class CanchaCreate(BaseModel):
    nombre: str
    techada: bool
     # Validación para evitar nombres vacíos
    @field_validator("nombre")
    def validate_nombre(cls, value):
        if not value.strip():
            raise ValueError("El nombre de la cancha no puede estar vacío.")
        return value

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

class ReservaUpdate(BaseModel):
    dia: str
    hora: str
    duracion: int
    telefono: Optional[str]
    nombre_contacto: Optional[str]  
    cancha_id: int

    # Validador para el campo 'dia'
    @field_validator("dia")
    def validate_dia(cls, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("El formato de la fecha debe ser 'YYYY-MM-DD'.")
        return value

    # Validador para el campo 'hora'
    @field_validator("hora")
    def validate_hora(cls, value):
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValueError("El formato de la hora debe ser 'HH:MM'.")
        return value

class CanchaResponse(BaseModel):
    id: int
    nombre: str
    techada: bool

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
