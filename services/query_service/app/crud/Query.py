import uuid
from core.db import session
from sqlalchemy.orm import Session
from models.QueryTable import QueryTable
from schemas.QuerySchema import QueryTableSchema

def read_by_id(id: uuid.UUID, db:Session = session):
    archives = db.query(QueryTable).filter(
        QueryTable.id == id
    ).first()

    return archives

def create_query(data: QueryTableSchema, db:Session = session):
    new_query = QueryTable(**data.model_dump())
    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    return new_query