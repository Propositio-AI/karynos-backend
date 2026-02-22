import uuid
from fastapi import APIRouter, Depends, HTTPException

from models.ArchiveTable import ArchiveTableSchema
from crud.Archive import archive_crud
from shared.utils import convert_to_filter
from shared.lib.gRPC import gRPC_Client

# /api/v1/archive
router = APIRouter()

@router.get("/", response_model=list[ArchiveTableSchema])
async def _(data: ArchiveTableSchema = Depends(), op = "=="):
    filters = convert_to_filter(data, op)
    response = archive_crud.read(filters)

    if response["success"]:
        return response["data"]
    else:
        HTTPException(status_code=500, detail=response["message"])

@router.get("/{archive_id}", response_model=ArchiveTableSchema)
async def _(archive_id: uuid.UUID):
    response = archive_crud.read([
        ["id", "==", archive_id]
    ])

    if not response["success"]:
        return HTTPException(status_code=500, detail=response["message"])
    
    return response["data"][0]
    
@router.post("/", response_model=ArchiveTableSchema)
async def _(data: ArchiveTableSchema):
    response = archive_crud.create(data)

    if not response["success"]:
        return HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]

@router.put("/", response_model=list[ArchiveTableSchema])
async def _(data: ArchiveTableSchema):
    response = archive_crud.update(
        [
            ["id", "==", data.id]
        ],
        {
            "contents": data.contents
        }
    )

    if not response["success"]:
        return HTTPException(status_code=500, detail=response["message"])
    
    return response["data"]


@router.post("/textbook/structure", response_model=ArchiveTableSchema)
async def _(data: ArchiveTableSchema):
    # ペルソナの取得
    net_response = gRPC_Client("Persona").call("CreatePersona", {})
    if net_response["success"]:
        server_response = net_response["data"]

        # TODO: サーバー側エラーの処理
        if not server_response["success"]:
            pass
        persona = server_response["data"]

    else: return HTTPException(status_code=500, detail=net_response["message"])

    # 教科書構成の作成
    net_response = gRPC_Client("TextBook").call("GenerateStructure", {
        "persona": persona,
        "query": data.contents["notion"]
    })
    if net_response["success"]:
        server_response = net_response["data"]

        # TODO: サーバー側エラーの処理
        if not server_response["success"]:
            pass
        structures = server_response["data"]

    else: return HTTPException(status_code=500, detail=net_response["message"])

    new_contents = data.contents
    new_contents["structures"] = structures
    update_response = archive_crud.update(
        [
            ["id", "==", data.id]
        ],
        {
            "contents": new_contents,
            "archive_status": "RUNNING"
        }
    )

    if not update_response["success"]:
        return HTTPException(status_code=500, detail=update_response["message"])
    
    return update_response["data"][0]