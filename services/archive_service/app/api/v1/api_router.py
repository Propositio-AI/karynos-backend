# Routing file

import uuid
from fastapi import APIRouter
from schemas.ArchiveSchema import newArchiveModel

router = APIRouter()

@router.get("/{archive_id}")
async def getArchive(archive_id: uuid.UUID):
    pass

@router.post("/")
async def newArchive(data: newArchiveModel):
    pass

