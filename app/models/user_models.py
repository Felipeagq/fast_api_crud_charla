from sqlalchemy import Column, Integer, String
from app.db.config import Base

class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)