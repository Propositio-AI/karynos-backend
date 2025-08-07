import uuid
from core.db import session
from sqlalchemy.orm import Session
from models.ArchiveTable import ArchiveTable
from schemas.ArchiveSchema import ArchiveTableSchema

def read_by_id(id: uuid.UUID, db:Session = session):
    archives = db.query(ArchiveTable).filter(
        ArchiveTable.id == id
    ).first()

    return archives

def create_archive(data: ArchiveTableSchema, db:Session = session):
    new_arvhie = ArchiveTable(**data.model_dump())
    db.add(new_arvhie)
    db.commit()
    db.refresh(new_arvhie)

    return new_arvhie