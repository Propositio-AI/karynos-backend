from fastapi import APIRouter

from shared.lib.gRPC.client import gRPC_Client
from shared.lib.websocket import WebSocketManager, streamer
from shared.lib.api_client import HTTP_APIClient

from pydantic import BaseModel

# /ws/v1/archive
router = APIRouter()
WsManager = WebSocketManager(router)

http_client = HTTP_APIClient()


class TextBookArchiveShema(BaseModel):
    archive_id: str
    notion: str
@WsManager.websocket("/textbook", TextBookArchiveShema)
async def _(data: TextBookArchiveShema, manager: WebSocketManager):
    # アーカイブ更新処理

    print("STAT TEXT", flush=True)
    # LLMで教科書を逐次生成
    async def handle_res(res):
        print(res)
        await manager.send_data({
            "contents": {
                "page": res
            }
        })
    await streamer(
        lambda: gRPC_Client("TextBook").call_server_stream("GenerateTextbook", {
            "query": data.notion,
        }),
        handle_res
    )


    # アーカイブ更新処理