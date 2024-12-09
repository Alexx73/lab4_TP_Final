from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, timedelta

from db import Session, get_db
from modelos import Cancha, Reserva
from schemas import CanchaCreate, CanchaUpdate, ReservaCreate,ReservaResponse
# from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
import locale
from sqlalchemy import cast, Time



# Establecer el idioma a español
try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Para Windows
except locale.Error:
        raise RuntimeError("No se pudo establecer el locale a español. Verifica la configuración de tu sistema.")

# Crear la aplicación FastAPI
app = FastAPI()

# Endpoint para obtener todas las reservas
@app.get("/reservas")
async def get_reservas(db: Session = Depends(get_db)):
    reservas = db.query(Reserva).all()
    return reservas


@app.delete("/reservas/{reserva_id}")
async def del_reservas(reserva_id: int, db: Session = Depends(get_db)):
     # Buscar la reserva por id
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Eliminar la reserva
    db.delete(db_reserva)
    db.commit()    
    raise HTTPException(
            status_code=200,
            detail=f"la reserva id: {reserva_id} ha sido borrada")


# Falta Endpoint para Modificar reservas
    


# Endpoint para crear una nueva reserva
# @app.post("/reservas", response_model=dict)
@app.post("/reservas", response_model=ReservaResponse)
def create_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    try:
        print(f"Datos recibidos: {reserva.dict()}")

         # Convertir la fecha "dia" con el formato DD-MM-YYYY
        dia = datetime.strptime(reserva.dia, "%d-%m-%Y")

         # Obtener el nombre del día de la semana en español
        dia_semana = dia.strftime("%A").capitalize()  # Capitaliza para empezar con mayúscula
        duracion = timedelta(minutes=reserva.duracion)
        duracion_minutos = int(duracion.total_seconds() - 1)  # Conversión a minutos
        
        print(f'Día procesado: {dia.strftime("%d-%m-%Y")}, Dia: {dia_semana}, duracion { duracion_minutos} ')

         # Calcular hora_fin
        try:
            # Intentar parsear con formato "HH:MM:SS"
            hora_inicio = datetime.strptime(reserva.hora, "%H:%M:%S").time()
        except ValueError:
         # Si falla, intentar con formato "HH:MM"
            try:
                hora_inicio = datetime.strptime(reserva.hora, "%H:%M").time()
            except ValueError:
                raise HTTPException(
            status_code=400, detail="Formato de hora inválido. Debe ser 'HH:MM' o 'HH:MM:SS'."
        )
        # hora_inicio = datetime.strptime(reserva.hora, "%H:%M").time()
        duracion_minutos = (reserva.duracion * 60) - 1  # Convertir horas a minutos y restar 1
        hora_fin = (datetime.combine(dia, hora_inicio) + timedelta(minutes=duracion_minutos)).time()
       

        # Normalizar y validar formato de hora
        hora_str = reserva.hora.strip()
        try:
            # Intentar parsear con formato "HH:MM:SS"
            hora_inicio = datetime.strptime(hora_str, "%H:%M:%S")
        except ValueError:
            # Si falla, intentar con formato "HH:MM"
            try:
                hora_inicio = datetime.strptime(hora_str, "%H:%M")
            except ValueError:
                raise ValueError("Formato de hora inválido. Debe ser 'HH:MM' o 'HH:MM:SS'.")
            
        hora_fin_reserva = hora_inicio + timedelta(minutes=duracion_minutos)
        # hora_fin = hora_inicio + timedelta(hora_inicio + reserva.duracion - 1)

        print(f"Hora Inicio: {hora_inicio.strftime('%H:%M')} hora fin Reserva: {hora_fin_reserva.strftime('%H:%M')} , duracion { duracion_minutos}")

        #####

       # Validar si hay solapamiento de reservas
        reservas_existentes = db.query(Reserva).filter(
        Reserva.cancha_id == reserva.cancha_id,
        Reserva.dia == dia,
        or_(
            and_(
                Reserva.hora <= cast(hora_inicio, Time),  # Convertir hora_inicio a Time
                Reserva.hora_fin > cast(hora_inicio, Time)
            ),
            and_(
                Reserva.hora < cast(hora_fin, Time),  # Convertir hora_fin a Time
                Reserva.hora_fin >= cast(hora_fin, Time)
            ),
            and_(
                Reserva.hora >= cast(hora_inicio, Time),
                Reserva.hora_fin <= cast(hora_fin, Time)
            )
        )
    ).first()

        if reservas_existentes:
            raise HTTPException(
                status_code=400, detail="La reserva se solapa con una existente."
            )
        
          #####
        
        # # Crear la nueva reserva
        nueva_reserva = Reserva(
            dia=dia,
            hora=hora_inicio,
            duracion=reserva.duracion,
            hora_fin=hora_fin,  # Almacenar hora_fin en la base de datos
            telefono=reserva.telefono,
            nombre_contacto=reserva.nombre_contacto,
            cancha_id=reserva.cancha_id,
        )

        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)
        return nueva_reserva

  
        # Ejemplo de retorno temporal
        # return {
        #     "message": "Reserva creada exitosamente",
        #     "dia_semana": dia_semana,  # Día de la semana (e.g., Monday, Tuesday)
        #     "dia": reserva.dia,
        #     # "hora": str(hora_inicio.time()),
        #      "hora_inicio": hora_inicio.strftime("%H:%M"),  # Formato solo horas y minutos
        #      "hora_fin": nueva_reserva.hora_fin.strftime("%H:%M"),
        #     "duracion": reserva.duracion,
        #     "telefono": reserva.telefono,
        #     "nombre_contacto": reserva.nombre_contacto,
        #     "cancha_id": reserva.cancha_id,
        # }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error en la creación de la reserva: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




# **********  Endpoint Canchas  **********
@app.get("/canchas")
async def get_canchas(db: Session = Depends(get_db)):
    canchas = db.query(Cancha).all()
    return canchas


@app.post("/canchas/", response_model=CanchaCreate)
def create_cancha(cancha: CanchaCreate, db: Session = Depends(get_db)):
    db_cancha = Cancha(nombre=cancha.nombre, techada=cancha.techada)
    db.add(db_cancha)
    db.commit()
    db.refresh(db_cancha)
    return db_cancha


@app.patch("/canchas/{cancha_id}", response_model=CanchaUpdate)
def update_cancha(cancha_id: int, cancha: CanchaUpdate, db: Session = Depends(get_db)):
    db_cancha = db.query(Cancha).filter(Cancha.id == cancha_id).first()
    if not db_cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    db_cancha.nombre = cancha.nombre
    db_cancha.techada = cancha.techada
    db.commit()
    db.refresh(db_cancha)
    return db_cancha


@app.delete("/canchas/{cancha_id}", response_model=dict)
def delete_cancha(cancha_id: int, db: Session = Depends(get_db)):
    # Buscar la cancha por id
    db_cancha = db.query(Cancha).filter(Cancha.id == cancha_id).first()
    if not db_cancha:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    # Eliminar la cancha
    db.delete(db_cancha)
    db.commit()    
    return {"message": f"La cancha con id {cancha_id} fue eliminada exitosamente"}





@app.get("/mess")
async def get_message():
    return {"message1": "Que haces putin"}


@app.get("/")
async def root():
    return {"message": "Hello World"}