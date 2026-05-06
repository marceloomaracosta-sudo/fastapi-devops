from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String  # tipos de columnas para la tabla
from sqlalchemy.ext.declarative import declarative_base  # base para definir modelos de tablas
from sqlalchemy.orm import sessionmaker, Session  # manejo de sesiones con la base de datos
from fastapi import Depends  # para inyectar dependencias en los endpoints
import os  # para leer variables de entorno

# lee la URL de conexión a la base de datos desde una variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# crea el motor de conexión a PostgreSQL usando la URL
engine = create_engine(DATABASE_URL)

# crea una clase de sesión vinculada al motor, cada sesión es una "conversación" con la DB
SessionLocal = sessionmaker(bind=engine)

# clase base de la que van a heredar todos los modelos de tablas
Base = declarative_base()

# define el modelo de la tabla "tareas" en la base de datos
class Tarea(Base):
    __tablename__ = "tareas"             # nombre de la tabla en PostgreSQL
    id = Column(Integer, primary_key=True, index=True)  # columna id, clave primaria autoincrementable
    titulo = Column(String)              # columna titulo, texto libre

# crea la tabla en la base de datos si no existe todavía
Base.metadata.create_all(bind=engine)

# instancia principal de la aplicación FastAPI
app = FastAPI()

# función que abre una sesión con la DB y la cierra cuando termina el request
def get_db():
    db = SessionLocal()  # abre la sesión
    try:
        yield db          # la entrega al endpoint que la pidió
    finally:
        db.close()        # la cierra siempre, aunque haya un error

# endpoint GET: devuelve todas las tareas guardadas en la base de datos
@app.get("/tareas")
def listar_tareas(db: Session = Depends(get_db)):  # inyecta la sesión automáticamente
    return db.query(Tarea).all()  # consulta todas las filas de la tabla tareas

# endpoint POST: recibe un JSON con "titulo" y crea una tarea nueva en la DB
@app.post("/tareas")
def crear_tarea(tarea: dict, db: Session = Depends(get_db)):
    nueva = Tarea(titulo=tarea["titulo"])  # crea el objeto tarea con el titulo recibido
    db.add(nueva)      # lo agrega a la sesión (todavía no se guarda)
    db.commit()        # guarda los cambios en la base de datos
    db.refresh(nueva)  # actualiza el objeto con los datos que asignó la DB (como el id)
    return nueva       # devuelve la tarea creada con su id

# endpoint DELETE: recibe un id y elimina esa tarea de la base de datos
@app.delete("/tareas/{id}")
def borrar_tarea(id: int, db: Session = Depends(get_db)):
    tarea = db.query(Tarea).filter(Tarea.id == id).first()  # busca la tarea por id
    if not tarea:
        return {"error": "No existe"}  # si no la encuentra, devuelve error
    db.delete(tarea)   # marca la tarea para eliminar
    db.commit()        # confirma la eliminación en la base de datos
    return {"mensaje": "Eliminada"}  # confirma que se eliminó