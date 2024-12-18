from pydantic import BaseModel, field_validator, validator
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

    class Config:
        orm_mode = True  # Habilitar conversión desde objetos SQLAlchemy

class ReservaUpdate(BaseModel):
    dia: str
    hora: str  # Este campo se convertirá automáticamente a `time`
    duracion: int
    telefono: str
    nombre_contacto: str
    cancha_id: int

    # @field_validator("hora", mode="before")
    # def validar_hora(cls, value):
    #     """
    #     Valida y convierte el campo 'hora' a un objeto `time`, admitiendo formatos `HH:MM` y `HH:MM:SS`.
    #     """
    #     if isinstance(value, time):
    #         return value  # Si ya es un objeto `time`, no hacer nada
    #     if isinstance(value, str):
    #         try:
    #             if len(value.split(":")) == 2:  # Formato `HH:MM`
    #                 value += ":00"  # Agregar segundos
    #             return datetime.strptime(value, "%H:%M:%S").time()  # Convertir a objeto `time`
    #         except ValueError:
    #             raise ValueError("El formato de hora debe ser 'HH:MM' o 'HH:MM:SS'.")
    #     raise ValueError("El campo 'hora' debe ser un string o un objeto `time`.")

    # @field_validator("dia", mode="before")
    # def validar_dia(cls, value):
    #     """
    #     Valida que el día esté en formato correcto 'YYYY-MM-DD'.
    #     """
    #     try:
    #         return datetime.strptime(value, "%Y-%m-%d").date()
    #     except ValueError:
    #         raise ValueError("El formato de la fecha debe ser 'YYYY-MM-DD'.")

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
