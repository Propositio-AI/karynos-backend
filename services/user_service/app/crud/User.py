from sqlalchemy.orm import Session

from core.db import session
from models.UserTable import UserTable
from schemas.UserSchema import UserTableSchema

def create_user(data: UserTableSchema, db: Session = session):
    new_user = UserTable(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def read_user_by_email(email: str, db: Session = session):
    user = db.query(UserTable).filter(
                UserTable.email == email,
            ).first()
        
    return user
