import uuid
from crud.Archive import read_by_id, create_archive
from schemas.ArchiveSchema import newArchiveSchema, ArchiveTableSchema

def get_archive(id: uuid.UUID):
    return read_by_id(id)

def add_archive(data: newArchiveSchema):
    #TODO ユーザーIDを取得する処理

    return create_archive(ArchiveTableSchema(**data.model_dump()))