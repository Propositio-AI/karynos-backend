import uuid
from fastapi import APIRouter, Depends

from models.ArchiveTable import ArchiveTableSchema
from crud.Archive import archive_crud
from shared.utils import convert_to_filter

# /api/v1/archive
router = APIRouter()

@router.get("/", response_model=list[ArchiveTableSchema])
async def _(data: ArchiveTableSchema = Depends(), op = "=="):
    filters = convert_to_filter(data, op)
    return archive_crud.read(filters)

@router.get("/{archive_id}", response_model=ArchiveTableSchema)
async def _(archive_id: uuid.UUID):
    return archive_crud.read([
        ["id", "==", archive_id]
    ])[0]    

@router.post("/", response_model=ArchiveTableSchema)
async def _(data: ArchiveTableSchema):
    return archive_crud.create(data)
