from fastapi import APIRouter
from pydantic import BaseModel

from shared.lib.gRPC import gRPC_Client
from shared.lib.websocket.websocket import WebSocketManager, streamer
from shared.lib.API import HTTP_APIClient
from crud.Archive import archive_crud
from models.ArchiveTable import ArchiveTableSchema

# /ws/v1/archive
router = APIRouter()
WsManager = WebSocketManager(router)

http_client = HTTP_APIClient()

@WsManager.websocket("/textbook", ArchiveTableSchema)
async def _(data: ArchiveTableSchema, manager: WebSocketManager):  
    # ペルソナの取得
    net_response = gRPC_Client("Persona").call("CreatePersona", {})    
    if(not net_response["success"]):
        manager.send_error(
            "",
            "\n".join(net_response["message"])
        )
    else:
        server_response = net_response["data"]
        
        if(not server_response["success"]):
            manager.send_error(
                "",
                "\n".join(server_response["message"])
            )
        persona = server_response["data"]


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