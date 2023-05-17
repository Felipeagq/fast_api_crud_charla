from sqlalchemy.orm import Session
from app.models.models import User
from app.schemas.schemas import UserSchema,RequestUser

def get_user(db:Session, skip:int=0, limit:int=100):
    print(db.query(User).offset(skip).limit(limit).all())
    return db.query(User).offset(skip).limit(limit).all()

def get_user_by_id(db:Session,user_id:int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db:Session, user:RequestUser):
    _user = User(
        username = user.username,
        email = user.email,
        password = user.password
    )
    db.add(_user)
    db.commit()
    db.refresh(_user)
    return _user

def remove_user(db:Session, user_id:int):
    _user = get_user_by_id(db=db,user_id=user_id)
    db.delete(_user)
    db.commit()
    return _user

def update_user(db:Session, user_id:int,
                username:str, email:str,password:str):
    _user = get_user_by_id(db=db, user_id=user_id)
    _user.username = username
    _user.email = email
    _user.password = password
    db.commit()
    db.refresh(_user)
    return _user