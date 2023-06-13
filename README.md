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
# app/db/config.py
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
# app/models/models.py
from sqlalchemy import Column, Integer, String
from app.db.config import Base

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
# app/schemas/schemas.py
from typing import List,Optional,Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

# creamos un tipo de variable "cualquiera"
T = TypeVar("T")

# Creamos el esquema del libro
class BookSchema(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    
    class Config:
        # le especificamos que será para uso de un ORM
        orm_mode = True
        # Colocamos un ejemplo que se mostrará en el SWAGGER
        schema_extra  = {
            "example":
                {
                    "id": 0,
                    "title": "titulo del libro",
                    "description": "decripción del libro"
                }
        }

# Creamos un schema de respuesta
class Response(BaseModel):
    code: str
    status: str
    message: str
    result: Optional[T]
````
Estos esquemas se usarám tanto para la entrada de nuestra API es decir será el tipo de datos que recibiremos como parametros y tambien lo usaremos en nuestra salida de nuestra API es decir que será la clase que retornaremos en el return de nuestra función.

## Creamos las funciones del CRUD
Nuestro CRUD y nuestra rutas estarán en archivos diferentes para cumplir con los principios SOLID.

````python
# app/db/crud.py
from sqlalchemy.orm import Session # La sesión de la DB
from app.models.models import Book # El modelo ORM de nuestra DB
from app.schemas.schemas import BookSchema # el esquema del JSON

# creamos la función para obtener todos los libros
def get_book(db:Session, skip:int=0, limit:int=100):
    return db.query(Book).offset(skip).limit(limit).all()
# query busca segun nuestro modelo
# skip es el salto o pasos que hace
# limit es la cantidad total de resultados que trae
# la función all trae todos los resultados 

def get_book_by_id(db:Session,book_id:int):
    return db.query(Book).filter(Book.id == book_id).first()
# buscamos los resultados del modelo 
# pero hacemos un filtro por el id
# obtenemos el primer resultado

def create_book(db:Session, book:BookSchema):
    _book = Book(
        title = book.title,
        description = book.description
    )
    db.add(_book)
    db.commit()
    db.refresh(_book)
    return _book
# creamos le damos las propiedades 
# asignando cada valor correspondiente del JSON al Modelo
# guardamos en la DB

def remove_book(db:Session, book_id:int):
    _book = get_book_by_id(db=db,book_id=book_id)
    db.delete(_book)
    db.commit()
    return _book
# para eliminar filtramos por el Id
# eliminamos

def update_book(db:Session, book_id:int,
                title:str, description:str):
    _book = get_book_by_id(db=db, book_id=book_id)
    _book.title = title
    _book.description = description
    db.commit()
    db.refresh(_book)
    return _book
    # filtramos por id 
    # reasignamos los valores de la entidad del modelo
    # guardamos los cambios en la DB
````

## Creamos las rutas de nuestra API
````python
# app/routes/routes.py
from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from app.db.config import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import BookSchema, Response, BookSchema

from app.db import crud

# Creamos un router, que es un conjunto de rutas agrupadas
router = APIRouter()

# Cabe mencionar que vamos a usar constantemente dos parametros 
# "request" el cual es la entrada y será acorde con el esquema "mostrar en SWAGGER"
# y "db" que es de tipo Sesion y de la cual depende de la conexión de nuestr db

# haremos uso de las funciones que creamos en el archivo de crud.py

# Creamos la ruta con la que crearemos 
@router.post("/create")
async def create_book_service(request: BookSchema, db: Session = Depends(get_db)):
    crud.create_book(db, book=request)
    print(request)
    return Response(status="Ok",
                    code="200",
                    message="Book created successfully",result=request).dict(exclude_none=True)
    # retornamos la respuesta con el schema de response


@router.get("/")
async def get_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    _books = crud.get_book(db, skip, limit)
    return Response(status="Ok", code="200", message="Success fetch all data", result=_books)


@router.patch("/update")
async def update_book(request: BookSchema, db: Session = Depends(get_db)):
    try:
        _book = crud.update_book(db, book_id=request.id,
                                title=request.title, description=request.description)
        return Response(status="Ok", code="200", message="Success update data", result=_book)
    except Exception as e:
        return Response(
            status="bad",
            code="304",
            message="the updated gone wrong"
        )
    # colocamos una excepción por si ocurre un error en la escritura en la db


@router.delete("/delete")
async def delete_book(request: BookSchema,  db: Session = Depends(get_db)):
    try:
        _book = crud.remove_book(db, book_id=book_id)
        return Response(status="Ok", code="200", message="Success delete data", result=_book)
    except Exception as e:
        return Response(
            status="bad",
            code="",
            message="the deleted gone wrong"
        )
    # colocamos una excepción por si ocurre un error en la escritura en la db
````
incluimos las rutas en nuestro archivo raiz, despues del ````app=FastAPI()```` 
````python
from fastapi import FastAPI
import uvicorn

import app.models.models as model
from app.db.config import engine
from app.routes.routes import router as router_crud

model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Book Details",
    description="You can perform CRUD operation by using this API",
    version="1.0.0"
)

@app.get("/")
def hello_world_check():
    return {
        "msg":"Hola Mundo"
    }

app.include_router(router=router_crud,tags=["CRUD"],prefix="/books")


if __name__ == "__main__":
    uvicorn.run("entrypoint:app",
                host="localhost",
                reload=True)
````
