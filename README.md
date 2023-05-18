# FASTAPI CRUD
FastAPI es un excelente framework de **Python 3.7+** diseñado para crear aplicaciones web de manera rápida y eficiente. Proporciona una combinación perfecta entre velocidad, facilidad de uso y rendimiento, lo que lo convierte en una opción destacada para desarrolladores y empresas.

Una de las características sobresalientes de FastAPI es su velocidad. Está construido sobre **Starlette**, un framework asincrónico, tambien hace uso de librerias de tipado como **pydantic** y **typing** que ayudan a proporcionar verificación estática de tipos y simplifica la manipulación de entradas y salidas de API, lo que evita errores y mejora la calidad del código. Ademas su integración con la especificación **OpenAPI** y la generación automática de documentación detalla e interactiva, hace que la colaboración con otros desarrolladores sea mucho más facil y fluida. y también admite la **autenticación y autorización**, permitiendo proteger las rutas y asegurar el acceso a recursos sensibles.

En este BLog realizaremos un CRUD con esta librería **FastAPI** y con la libreria ORM de **SQLAlchemy**,n haciendo uso de esquemas y Modelos con la base de datos local de SQLite y haciendo uso de laarquitectura limpia.

## Entorno virtual
Lo primero que vamos hacer es crear un entorno virtual para instalar todas nuestras librerias.
````shell
# haciendo uso de gitbash
python -m virtualenv venv

source venv/Script/activate
````

## Instalamos las librerias requeridas
````shell
pip install fastapi uvicorn sqlalchemy psycopg2 fastapi-utils
````

## Creamos la ruta raiz
Lo primero que vamos a crear es una ruta raiz en un archivo llamado entrypoint el cual será el punto de entrada para toda nuestra API.
````python
# Entrypoint.py

# importación de librerias
from fastapi import FastAPI
import uvicorn

# Creación de la aplicación
app = FastAPI()

# Ruta raiz
@app.get("/")
def hello_world_check():
    return {
        "msg":"Hola Mundo"
    }

# Comando para correr la app si es el archivo principal
if __name__ == "__main__":
    uvicorn.run("entrypoint:app",
                host="localhost",
                reload=True)
````
La ruta raíz generalmente se maneja como un **Health check** o ruta de bienestar, esto quiere decir si esa ruta funciona, nuestra API está levantada y lista para aceptar peticiones.

## Creación del archivo de configuración de BD
Luego procederemos a la configuración de la Base de datos de nuestro proyecto, para eso haremos uso de la libreria de SQLAlchemy para manipular una base de datos local de SQLite.
````python
# app/Config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ruta de la base de datos 
DATABASE_URL = "sqlite:///books.db"

# Creamos el motor, el cual al comienzo de la ruta de la DB
# Se especifica que es sqlite
engine = create_engine(DATABASE_URL,
                    connect_args={"check_same_thread": False}
                    )

# Luego creamos los parametros para las sessiones que se creen de dicho motor
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

# Creamos el mapeador ORM 
Base = declarative_base()

 # Creamos la función para el uso de session de la DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
````

## Creación de los modelos para la DB
Luego de configurar la base de datos, procederemos a crear nuestro modelos para que el mapeador de SQLAlchemy, pueda crear las tablas a partir de esos modelos.
````python
# app/models.py
from sqlalchemy import Column, Integer, String
from app.config import Base

# clase 
class Book(Base):
    # nombre de la tabla
    __tablename__ = "book"
    
    # Las columnas de nuestra tabla y el tipo de dato de cada una
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
````
Agreamos la configuración y los modelos en el archivo raiz, antes del ````app=FastAPI()```` , para que cuando arranque nuestra app, esta mapee el modelo y lo cree en la db
````python 
#entrypoint.py
import app.models as model # importamos todos los modelos dentro del archivo
from app.config import engine

# El motor mapea y crea el modelo en la DB
model.Base.metadata.create_all(bind=engine)
````


|Aqui podemos ver que la tabla y las columnas se crearon en la base de datos|
|-|

## Creamos el archivo de Schemas
Ya habiendo creado la base de datos, vamos a proceder a estructurar las entradas y salidas de nuestra API, para eso usaremos una libreria llamada pydantic y typing que nos permitiran crear una clase con elementos tipados que luego FastAPI mapeará en el JSON que se usará en dichas entradas y salidas
````python 
# app/schemas.py
from typing import List,Optional,Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")

class BookSchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        orm_mode = True


class RequestBook(BaseModel):
    parameter: BookSchema = Field(...)


class Response(BaseModel):
    code: str
    status: str
    message: str
    result: Optional[T]
````

## Creamos las funciones del CRUD
````python
from sqlalchemy.orm import Session
from app.models import Book
from app.schemas import BookSchema

def get_book(db:Session, skip:int=0, limit:int=100):
    return db.query(Book).offset(skip).limit(limit).all()

def get_book_by_id(db:Session,book_id:int):
    return db.query(Book).filter(Book.id == book_id).first()

def create_book(db:Session, book:BookSchema):
    _book = Book(
        title = book.title,
        description = book.description
    )
    db.add(_book)
    db.commit()
    db.refresh(_book)
    return _book

def remove_book(db:Session, book_id:int):
    _book = get_book_by_id(db=db,book_id=book_id)
    db.delete(_book)
    db.commit()
    return _book

def update_book(db:Session, book_id:int,
                title:str, description:str):
    _book = get_book_by_id(db=db, book_id=book_id)
    _book.title = title
    _book.description = description
    db.commit()
    db.refresh(_book)
    return _book
````

## Creamos las rutas de nuestra API
````python
# app/routes.py
from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from app.config import SessionLocal
from sqlalchemy.orm import Session
from app.schemas import BookSchema, Response, RequestBook

from app import crud    

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create")
async def create_book_service(request: RequestBook, db: Session = Depends(get_db)):
    crud.create_book(db, book=request.parameter)
    return Response(status="Ok",
                    code="200",
                    message="Book created successfully").dict(exclude_none=True)


@router.get("/")
async def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    _books = crud.get_book(db, skip, limit)
    return Response(status="Ok", code="200", message="Success fetch all data", result=_books)


@router.patch("/update")
async def update_book(request: RequestBook, db: Session = Depends(get_db)):
    _book = crud.update_book(db, book_id=request.parameter.id,
                            title=request.parameter.title, description=request.parameter.description)
    return Response(status="Ok", code="200", message="Success update data", result=_book)


@router.delete("/delete")
async def delete_book(request: RequestBook,  db: Session = Depends(get_db)):
    crud.remove_book(db, book_id=request.parameter.id)
    return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)
````
incluimos las rutas en nuestro archivo raiz, despues del ````app=FastAPI()```` 
````python
app.include_router(router=router_crud,tags=["CRUD"],prefix="/books")
````
