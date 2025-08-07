import uuid
from fastapi import APIRouter

from schemas.ArchiveSchema import newArchiveSchema
from api.v1.endpoints.archive import get_archive, add_archive

router = APIRouter()

@router.get("/{archive_id}")
async def _(archive_id: uuid.UUID):
    archive = get_archive(archive_id)
    
    return {
        "id": archive.id,
        "type": archive.type, 
        "share_type": archive.share_type,
        "contents": archive.contents,
        "metadata": archive.contents_metadata,
        "created_at": archive.created_at,
    }
    

@router.post("/")
async def _(data: newArchiveSchema):
    new_archive =  add_archive(data)

    return {
        "id": new_archive.id,
        "type": new_archive.type, 
        "share_type": new_archive.share_type,
        "contents": new_archive.contents,
        "metadata": new_archive.contents_metadata,
        "created_at": new_archive.created_at,
    }
