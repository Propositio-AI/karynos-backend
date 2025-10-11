from fastapi import APIRouter
from pydantic import BaseModel

from shared.lib.gRPC import gRPC_Client
from shared.lib.websocket.websocket import WebSocketManager, streamer
from shared.lib.api_client import HTTP_APIClient
from crud.Archive import archive_crud
from models.ArchiveTable import ArchiveTableSchema

# /ws/v1/archive
router = APIRouter()
WsManager = WebSocketManager(router)

http_client = HTTP_APIClient()

@WsManager.websocket("/textbook", ArchiveTableSchema)
async def _(data: ArchiveTableSchema, manager: WebSocketManager):  
    # ペルソナの取得
    netSuccess, netRes, netError = gRPC_Client("Persona").call("CreatePersona", {})    
    if(not netSuccess):
        manager.send_error(
            netError.code,
            netError.message
        )
    else:
        serverSuccess, persona, serverError = netRes
        
        if(not serverSuccess):
            manager.send_error(
                serverError.code,
                serverError.message
            )


    # LLMで教科書を逐次生成
    async def handle_res(res):
        print(res, flush=True)
        await manager.send_data({
            "elements": res
        })

        data.contents["elements"] = res
        archive_crud.update(
            [
                ["id", "==", str(data.id)]
            ],
            {
                "contents": data.contents   
            }
        )

    await streamer(
        lambda: gRPC_Client("TextBook").call_server_stream("GenerateElement", {
            "persona": persona,
            "structures": data.contents["structures"],
            "elements": data.contents["elements"]
        }),
        handle_res
    )

    archive_crud.update(
        [
            ["id", "==", str(data.id)]
        ],
        {
            "archive_status": "SUCCEEDED"   
        }
    )