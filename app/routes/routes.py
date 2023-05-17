from fastapi import APIRouter, HTTPException, Path
from fastapi import Depends
from app.db.config import SessionLocal
from sqlalchemy.orm import Session
from app.schemas.schemas import UserSchema, Response, RequestUser

from app.db import crud
from app.db.config import get_db

router = APIRouter()


@router.post("/create")
async def create_user_service(request: RequestUser, db: Session = Depends(get_db)):
    user = crud.create_user(db, user=request.parameter)
    return Response(status="Ok",
                    code="200",
                    message="Book created successfully",
                    result=user).dict(exclude_none=True)


@router.get("/")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    _users = crud.get_user(db, skip, limit)
    return Response(status="Ok", code="200", message="Success fetch all data", result=_users)


@router.patch("/update")
async def update_user(request: RequestUser, db: Session = Depends(get_db)):
    _user = crud.update_user(db, book_id=request.parameter.id,
                            title=request.parameter.title, description=request.parameter.description)
    return Response(status="Ok", code="200", message="Success update data", result=_user)


@router.delete("/delete")
async def delete_user(request: RequestUser,  db: Session = Depends(get_db)):
    crud.remove_user(db, book_id=request.parameter.id)
    return Response(status="Ok", code="200", message="Success delete data").dict(exclude_none=True)