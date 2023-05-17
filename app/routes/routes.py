from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from app.db.config import SessionLocal
from sqlalchemy.orm import Session
from app.schemas.schemas import BookSchema, Response, RequestBook

from app.db import crud
from app.db.config import get_db

router = APIRouter()


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