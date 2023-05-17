from fastapi import APIRouter, status, Depends, HTTPException

from app.schemas.user_schemas import UserSchemas

from sqlalchemy.orm import Session
from app.db.config import get_db
from app.models.user_models import UserModel

from app.settings.settings import Security



router = APIRouter(tags=["User management"])

@router.post("/user",status_code=status.HTTP_202_ACCEPTED)
def create_user(
    request: UserSchemas,
    db:Session = Depends(get_db)
)-> str:
    try:
        print(request)
        new_user = UserModel(
            username = request.username,
            email= request.email,
            # password= Security.get_password(request.password)
            password = request.password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "msg":"ok",
            "data":new_user
        }
    except Exception as e:
        print(f"\n\n {e} \n\n")
        return {
            "msg":"bad"
        }


@router.get("/user/{id}", 
            status_code=status.HTTP_200_OK)
def user_by_id(
    id:str,
    db:Session = Depends(get_db)
) -> str :
    user = db.query(UserModel).filter(UserModel.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user by id not found"
        )
    return user