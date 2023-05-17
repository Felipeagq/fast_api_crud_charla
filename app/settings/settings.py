from re import sub
from pydantic import BaseSettings, ValidationError
from typing import Union,Any
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status

import os

from passlib.context import CryptContext
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer

from app.schemas import blog_schema

class Settings(BaseSettings):
    PROJECT_NAME: str = "BACKEND API"
    PROJECT_VERSION: str = "v0.0.2"
    API_V1_STR: str = "/api/v1"

    # SQLALCHEMY_DATABASE_URL:str = "postgresql://postgres:postgres@localhost:5432"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*3
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = os.urandom(12).hex()

settings = Settings()

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer( tokenUrl=f"{settings.API_V1_STR}/login" )


class Security:

    def created_access_token(
        subject:Union[str,Any],
        expire_delta: timedelta = None
    ) -> str :
        if expire_delta:
            expire = datetime.utcnow() + expire_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                )
        to_encode ={
            "sub": str(subject),
            "exp": expire
        }
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )


    def is_valid(
        plain_password:str,
        hashed_password:str
    ) -> str:
        return password_context.verify(
            plain_password,
            hashed_password
        )


    def get_password(
        password:str
    ) -> str:
        return password_context.hash(password)




def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try: 
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        subjet = payload.get("sub")
        token_data= blog_schema.TokenData(id=subjet)
    except Exception as e:
        print(e)
        return e
    # user = QUERY_TO_DATABASE
    # if not user:
    #     raise Http
    # if token_data is None:
    #     raise credentials_exception
    
    return token_data
