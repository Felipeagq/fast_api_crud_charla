from typing import List,Optional,Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar("T")

class UserSchemas(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    
    class Config:
        orm_mode = True


class TokenData(BaseModel):
    id: str = None