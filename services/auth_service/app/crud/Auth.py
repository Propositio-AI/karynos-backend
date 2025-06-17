from sqlalchemy.orm import Session
from models.AuthTable import AuthTable
from schemas.AuthSchema import AuthSchema
from datetime import datetime

"""

get_*	取得（1件またはリスト）
create_*	新規作成
update_*	更新
delete_*	削除
exists_*, is_*	真偽判定や存在チェックなど

"""

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
