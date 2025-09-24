import uuid
from fastapi import APIRouter, Depends, HTTPException

from models.ArchiveTable import ArchiveTableSchema
from crud.Archive import archive_crud
from shared.utils import convert_to_filter
from shared.lib.gRPC.client import gRPC_Client

# /api/v1/archive
router = APIRouter()

@router.get("/", response_model=list[ArchiveTableSchema])
async def _(data: ArchiveTableSchema = Depends(), op = "=="):
    filters = convert_to_filter(data, op)
    success, result, error = archive_crud.read(filters)

    if success:
        return result
    else:
        HTTPException(status_code=500, detail=error)

@router.get("/{archive_id}", response_model=ArchiveTableSchema)
async def _(archive_id: uuid.UUID):
    success, result, error = archive_crud.read([
        ["id", "==", archive_id]
    ])

    if not success:
        return HTTPException(status_code=500, detail=error)
    
    return result[0]
    
@router.post("/", response_model=ArchiveTableSchema)
async def _(data: ArchiveTableSchema):
    success, result, error = archive_crud.create(data)

    if not success:
        return HTTPException(status_code=500, detail=error)
    
    return result

@router.put("/", response_model=list[ArchiveTableSchema])
async def _(data: ArchiveTableSchema):
    success, result, error = archive_crud.update(
        [
            ["id", "==", data.id]
        ],
        {
            "contents": data.contents
        }
    )

    if not success:
        return HTTPException(status_code=500, detail=error)
    
    return result


@router.post("/textbook/structure", response_model=ArchiveTableSchema)
async def _(data: ArchiveTableSchema):
    # ペルソナの取得
    netSuccess, netRes, netError = gRPC_Client("Persona").call("CreatePersona", {})
    if netSuccess:
        serverSuccess, persona, serverError = netRes

        # TODO: サーバー側エラーの処理
        if not serverSuccess:
            pass

    else: return HTTPException(status_code=500, detail=netError)

    # 教科書構成の作成
    netSuccess, netRes, netError = gRPC_Client("TextBook").call("GenerateStructure", {
        "persona": persona,
        "query": data.contents["notion"]
    })
    if netSuccess:
        serverSuccess, structures, serverError = netRes

        # TODO: サーバー側エラーの処理
        if not serverSuccess:
            pass

    else: return HTTPException(status_code=500, detail=netError)

    new_contents = data.contents
    new_contents["structures"] = structures
    success, new_archive, error = archive_crud.update(
        [
            ["id", "==", data.id]
        ],
        {
            "contents": new_contents,
            "archive_status": "RUNNING"
        }
    )

    if not success:
        return HTTPException(status_code=500, detail=error)
    
    return new_archive[0]