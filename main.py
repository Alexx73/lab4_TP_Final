from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session

from db import Session, get_db
from modelos import Cancha, Reserva
from schemas import CanchaCreate, CanchaUpdate, ReservaCreate,ReservaResponse, CanchaResponse, ReservaUpdate
# from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
import locale
from sqlalchemy import cast, Time
from fastapi.middleware.cors import CORSMiddleware

# Establecer el idioma a español
try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')  # Para Windows
except locale.Error:
        raise RuntimeError("No se pudo establecer el locale a español. Verifica la configuración de tu sistema.")

# Crear la aplicación FastAPI
app = FastAPI()

# Lista de orígenes permitidos
origins = [
    "http://localhost:5173",  # Cambia esto al puerto donde está corriendo tu frontend
    # Puedes agregar más orígenes si es necesario
]

# Añadir el middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir solo los orígenes especificados
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)




# Endpoint para obtener todas las reservas
@app.get("/reservas")
async def get_reservas(db: Session = Depends(get_db)):
    reservas = db.query(Reserva).all()
    return reservas

# Endpoint para obtener todas las reservas filtradas por día y cancha
@app.get("/reservas-por-dia")
async def get_reservas(dia: str, cancha_id: int = 0, db: Session = Depends(get_db)):
    try:
        # Convertir el parámetro dia a un objeto datetime
        fecha = datetime.strptime(dia, "%Y-%m-%d").date()

        if not dia:
            raise HTTPException(status_code=400, detail="Debe Ingresar una fecha valida, con este formato 'YYYY-MM-DD'.")

        # Construir la consulta
        if cancha_id > 0:
            # Filtrar por fecha y por ID de cancha
            reservas = db.query(Reserva).filter(
                and_(
                    Reserva.dia == fecha,
                    Reserva.cancha_id == cancha_id
                )
            ).all()
        else:
            # Filtrar solo por fecha (todas las canchas)
            reservas = db.query(Reserva).filter(Reserva.dia == fecha).all()

            # Validar si no hay reservas
        if not reservas:
            return {"message": f"No hay reservas para el día {fecha}."}

        return reservas

    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Debe ser 'YYYY-MM-DD'.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy import or_, and_, cast, Time
# from models import Reserva
# from schemas import ReservaUpdate, ReservaResponse
# from database import get_db
# from datetime import datetime, timedelta, time

# router = APIRouter()

@app.patch("/reservas/{reserva_id}", response_model=ReservaResponse)
async def mod_reservas(
    reserva_id: int,
    reserva: ReservaUpdate,  # Datos enviados por el cliente para actualizar
    db: Session = Depends(get_db)
):
    # Obtener la reserva existente
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not db_reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada.")

    # Definir horarios de apertura y cierre
    hora_apertura = time(14, 0)  # 14:00
    hora_cierre = time(22, 0)    # 22:00

    # Procesar fecha
    try:
        dia = datetime.strptime(reserva.dia, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="El formato de la fecha debe ser 'YYYY-MM-DD'."
        )

    # Procesar hora_inicio con tolerancia a formatos "%H:%M" y "%H:%M:%S"
    try:
        if ":" in reserva.hora:
            hora_inicio = datetime.strptime(reserva.hora, "%H:%M:%S").time()  # Intentar con segundos
        else:
            hora_inicio = datetime.strptime(reserva.hora, "%H:%M").time()  # Intentar sin segundos
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de hora inválido. Debe ser 'HH:MM' o 'HH:MM:SS'."
        )

    # Calcular hora_fin
    duracion_minutos = reserva.duracion * 60
    hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=duracion_minutos)).time()

    # Validar rango horario
    if not (hora_apertura <= hora_inicio <= hora_cierre):
        raise HTTPException(
            status_code=400,
            detail=f"La hora de inicio debe estar entre {hora_apertura.strftime('%H:%M')} y {hora_cierre.strftime('%H:%M')}."
        )
    if not (hora_apertura <= hora_fin <= hora_cierre):
        raise HTTPException(
            status_code=400,
            detail=f"La hora de fin debe estar entre {hora_apertura.strftime('%H:%M')} y {hora_cierre.strftime('%H:%M')}."
        )

    # Validar solapamiento de reservas
    reservas_existentes = db.query(Reserva).filter(
        Reserva.cancha_id == reserva.cancha_id,
        Reserva.dia == dia,
        Reserva.id != reserva_id,  # Excluir la reserva actual
        or_(
            and_(Reserva.hora <= cast(hora_inicio, Time), Reserva.hora_fin > cast(hora_inicio, Time)),
            and_(Reserva.hora < cast(hora_fin, Time), Reserva.hora_fin >= cast(hora_fin, Time)),
            and_(Reserva.hora >= cast(hora_inicio, Time), Reserva.hora_fin <= cast(hora_fin, Time))
        )
    ).first()

    if reservas_existentes:
        raise HTTPException(
            status_code=400,
            detail="La reserva se solapa con una existente."
        )

    # Actualizar la reserva existente
    db_reserva.nombre_contacto = reserva.nombre_contacto
    db_reserva.telefono = reserva.telefono
    db_reserva.dia = dia
    db_reserva.hora = hora_inicio
    db_reserva.duracion = reserva.duracion
    db_reserva.hora_fin = hora_fin
    db_reserva.cancha_id = reserva.cancha_id

    db.commit()
    db.refresh(db_reserva)

    return db_reserva



# Endpoint para crear una nueva reserva
# @app.post("/reservas", response_model=dict)
@app.post("/reservas", response_model=ReservaResponse)
def create_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    try:
        print(f"Datos recibidos: {reserva}")

        # Definir horarios de apertura y cierre
        hora_apertura = time(14, 0)
        hora_cierre = time(22, 0)

        # Procesar la fecha
        try:
            dia = datetime.strptime(reserva.dia, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="El formato de la fecha debe ser 'YYYY-MM-DD'."
            )

        # Procesar la hora de inicio con tolerancia para formatos "%H:%M" y "%H:%M:%S"
        try:
            if len(reserva.hora.split(":")) == 2:
                hora_inicio = datetime.strptime(reserva.hora, "%H:%M").time()  # Formato HH:MM
            elif len(reserva.hora.split(":")) == 3:
                hora_inicio = datetime.strptime(reserva.hora, "%H:%M:%S").time()  # Formato HH:MM:SS
            else:
                raise ValueError("Formato inválido")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de hora inválido. Debe ser 'HH:MM' o 'HH:MM:SS'."
            )

        # Calcular la hora de fin
        duracion_minutos = reserva.duracion * 60  # Convertir duración a minutos
        hora_fin = (datetime.combine(datetime.today(), hora_inicio) + timedelta(minutes=duracion_minutos)).time()

        print(f"Fecha procesada: {dia}, Hora inicio: {hora_inicio}, Hora fin: {hora_fin}")

        # Validar rango horario
        if not (hora_apertura <= hora_inicio <= hora_cierre):
            raise HTTPException(
                status_code=400,
                detail=f"La hora de inicio debe estar entre {hora_apertura} y {hora_cierre}."
            )
        if not (hora_apertura <= hora_fin <= hora_cierre):
            raise HTTPException(
                status_code=400,
                detail=f"La hora de fin debe estar entre {hora_apertura} y {hora_cierre}."
            )

        # Validar solapamiento de reservas
        reservas_existentes = db.query(Reserva).filter(
            Reserva.cancha_id == reserva.cancha_id,
            Reserva.dia == dia,
            or_(
                and_(Reserva.hora <= hora_inicio, Reserva.hora_fin > hora_inicio),
                and_(Reserva.hora < hora_fin, Reserva.hora_fin >= hora_fin),
                and_(Reserva.hora >= hora_inicio, Reserva.hora_fin <= hora_fin)
            )
        ).first()

        if reservas_existentes:
            raise HTTPException(
                status_code=400,
                detail="La reserva se solapa con una existente."
            )

        # Crear la reserva
        nueva_reserva = Reserva(
            dia=dia,
            hora=hora_inicio,
            duracion=reserva.duracion,
            hora_fin=hora_fin,
            telefono=reserva.telefono,
            nombre_contacto=reserva.nombre_contacto,
            cancha_id=reserva.cancha_id,
        )
        db.add(nueva_reserva)
        db.commit()
        db.refresh(nueva_reserva)

        return nueva_reserva

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error en la creación de la reserva: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")






# **********  Endpoint Canchas  **********
@app.get("/canchas")
async def get_canchas(db: Session = Depends(get_db)):
    canchas = db.query(Cancha).order_by(Cancha.nombre.asc()).all()
    return canchas


@app.post("/canchas/", response_model=CanchaResponse)
def create_cancha(cancha: CanchaCreate, db: Session = Depends(get_db)):
    # Verificar si el nombre ya existe
    existing_cancha = db.query(Cancha).filter(Cancha.nombre == cancha.nombre).first()
    if existing_cancha:
        raise HTTPException(status_code=400, detail="El nombre de la cancha ya está en uso.")

    # Crear la nueva cancha
    db_cancha = Cancha(nombre=cancha.nombre, techada=cancha.techada)

    # Guardar en la base de datos
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