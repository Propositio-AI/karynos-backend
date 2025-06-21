import uuid
from fastapi import APIRouter
from schemas.ArchiveSchema import newArchiveModel

from api.v1.endpoints.archive import get_archive, create_archive

router = APIRouter()

@router.get("/{archive_id}")
async def getArchive(archive_id: uuid.UUID):
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
async def newArchive(data: newArchiveModel):
    create_archive(data)

