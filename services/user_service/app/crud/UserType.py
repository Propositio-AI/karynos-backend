from sqlalchemy.orm import Session
from models.UserTypeTable import UserTypeTable
from schemas.UserTypeSchema import UserTypeTable

def create_user_type(db: Session, data: UserTypeTable):
    new_user = UserTypeTable(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user