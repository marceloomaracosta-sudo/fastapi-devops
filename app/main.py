import time

# espera hasta que la base de datos esté lista antes de arrancar
def esperar_db():
    import psycopg2
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("Base de datos lista")
            break
        except Exception:
            print("Esperando base de datos...")
            time.sleep(2)

from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import time
import logging

# configura el sistema de logs para mostrar fecha, nivel y mensaje
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# espera hasta que la base de datos esté lista antes de arrancar
def esperar_db():
    import psycopg2
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            logger.info("Base de datos lista")
            break
        except Exception:
            logger.warning("Esperando base de datos...")
            time.sleep(2)

esperar_db()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/tareas")
def listar_tareas(db: Session = Depends(get_db)):
    logger.info("GET /tareas - listando todas las tareas")
    return db.query(Tarea).all()

@app.post("/tareas")
def crear_tarea(tarea: dict, db: Session = Depends(get_db)):
    logger.info(f"POST /tareas - creando tarea: {tarea}")
    nueva = Tarea(titulo=tarea["titulo"])
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.delete("/tareas/{id}")
def borrar_tarea(id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /tareas/{id} - intentando borrar tarea")
    tarea = db.query(Tarea).filter(Tarea.id == id).first()
    if not tarea:
        logger.warning(f"DELETE /tareas/{id} - tarea no encontrada")
        return {"error": "No existe"}
    db.delete(tarea)
    db.commit()
    logger.info(f"DELETE /tareas/{id} - tarea eliminada correctamente")
    return {"mensaje": "Eliminada"}