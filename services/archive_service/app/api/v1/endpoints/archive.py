import uuid
from crud.Archive import read_by_id, create_archive
from schemas.ArchiveSchema import newArchiveModel, ArchiveSchema

def get_archive(id: uuid.UUID):
    return read_by_id(id)

def add_archvie(data: newArchiveModel):
    create_archive(ArchiveSchema(**data.model_dump()))