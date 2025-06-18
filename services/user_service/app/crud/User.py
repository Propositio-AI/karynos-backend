from sqlalchemy.orm import Session
from models.UserTable import UserTable
from schemas.UserSchema import UserSchema

def create_user(db: Session, data: UserSchema):
    new_user = UserTable(**data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def get_user_by_email(db: Session, email: str):
    user = db.query(UserTable).filter(
        UserTable.email == email,
        ).first()
    
    if user is not None:
        pass
    
    return user
