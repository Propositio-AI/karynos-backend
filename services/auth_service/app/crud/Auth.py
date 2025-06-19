from sqlalchemy.orm import Session
from models.AuthTable import AuthTable
from schemas.AuthSchema import AuthSchema
from datetime import datetime

def create_token(db: Session, data: AuthSchema):
    new_token = AuthTable(**data.model_dump())
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return new_token

def get_valid_token(db: Session, token: str, vertify_time: datetime):
    valid_token = db.query(AuthTable).filter(
        AuthTable.token == token,
        AuthTable.expires_at >= vertify_time,
        AuthTable.used_at == None
        ).first()
    
    if valid_token is not None:
        valid_token.used_at = vertify_time
        db.commit()
        db.refresh(valid_token)
    
    return valid_token
