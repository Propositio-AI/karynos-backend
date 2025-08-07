from sqlalchemy.orm import Session
from core.db import session
from models.UserTypeTable import UserTypeTable
from schemas.UserTypeSchema import UserTypeTableSchema

def create_user_type(data: UserTypeTableSchema, db: Session = session):
    new_user = UserTypeTable(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user