# FASTAPI CRUD

## Instalamos las librerias requeridas
````shell
pip install fastapi uvicorn sqlalchemy psycopg2 fastapi-utils
````

## Creamos la ruta raiz
````python
# Entrypoint.py
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def hello_world_check():
    return {
        "msg":"Hola Mundo"
    }


if __name__ == "__main__":
    uvicorn.run("entrypoint:app",
                host="localhost",
                reload=True)
````
## Creación del archivo de configuración de BD
````python
# app/Config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///books.db"

engine = create_engine(DATABASE_URL,
                    connect_args={"check_same_thread": False}
                    )

SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

Base = declarative_base()
````

## Creación de los modelos para la DB
````python
# app/models.py
from sqlalchemy import Column, Integer, String
from app.config import Base

class Book(Base):
    __tablename__ = "book"
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
````
Agreamos la configuración y los modelos en el archivo raiz, antes del ````app=FastAPI()```` 
````python 
#entrypoint.py
import app.models as model
from app.config import engine

model.Base.metadata.create_all(bind=engine)
````

## Creamos el archivo de Schemas
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
