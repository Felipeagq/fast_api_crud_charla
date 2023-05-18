from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from app.db.config import SessionLocal,get_db
from sqlalchemy.orm import Session
from app.schemas.schemas import BookSchema, Response, BookSchema

from app.db import crud

router = APIRouter()


@router.post("/create")
async def create_book_service(request: BookSchema, db: Session = Depends(get_db)):
    crud.create_book(db, book=request)
    print(request)
    return Response(status="Ok",
                    code="200",
                    message="Book created successfully",result=request).dict(exclude_none=True)


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


@router.delete("/delete")
async def delete_book(request: BookSchema,  db: Session = Depends(get_db)):
    try:
        crud.remove_book(db, book_id=request.id)
        return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)
    except Exception as e:
        return Response(
            status="bad",
            code="",
            message="the deleted gone wrong"
        )