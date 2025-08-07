from sqlalchemy.orm import Session

from models.AuthTable import AuthTable
from schemas.AuthSchema import AuthTableSchema
from datetime import datetime
from core.db import session
from shared.utils.time import get_utc_time


def create_token(data: AuthTableSchema, db: Session = session):
    new_token = AuthTable(**data.model_dump())
    db.add(new_token)
    db.commit()
    db.refresh(new_token)

    return new_token

def read_valid_token(token: str, verify_time: datetime = get_utc_time(), db: Session = session):
    valid_token = db.query(AuthTable).filter(
        AuthTable.token == token,
        AuthTable.expires_at >= verify_time,
        AuthTable.used_at == None
    ).first()
    
    # 開発用にログイントークンを常に有効に
    # if valid_token is not None:
    #     valid_token.used_at = verify_time
    #     db.commit()
    #     db.refresh(valid_token)
    
    return valid_token
