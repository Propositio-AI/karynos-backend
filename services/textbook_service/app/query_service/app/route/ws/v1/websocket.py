from fastapi import APIRouter
from pydantic import BaseModel

from models.QueryTable import QueryTableSchema

from shared.lib.API import HTTP_APIClient
from shared.lib.gRPC import gRPC_Client
from shared.lib.websocket.websocket import WebSocketManager, streamer
from shared.lib.auth import get_default_user_id

# /ws/v1/query
router = APIRouter()
WsManager = WebSocketManager(router)

http_client = HTTP_APIClient()

class PlanQuerySchema(BaseModel):
    query: str
@WsManager.websocket("/plan", PlanQuerySchema)
async def _(data: PlanQuerySchema, manager: WebSocketManager):
    # ユーザーIDの取得（将来的にはWebSocketのヘッダーから取得）
    # ユーザーIDはDBに保存しないためこのタイミングでは必要ないが、ログとして残すなら必要になる
    # user_id = get_default_user_id()

    # ペルソナの取得
    net_response = gRPC_Client("Persona").call("CreatePersona", {})    
    if(not net_response["success"]):
        manager.send_error(
            "",
            "\n".join(net_response["message"])
        )

        return
    else:
        server_response = net_response["data"]
        if(not server_response["success"]):
            manager.send_error(
                "",
                "\n".join(server_response["message"])
            )

            return
        persona = server_response["data"]
    
    # LLMで学習プランを作成
    notions = ""
    async def handle_res(res):
        nonlocal notions
        notions += res
        await manager.send_data({
            "notions": notions.split("\n")
        })

    await streamer(
        lambda: gRPC_Client("TextBook").call_server_stream("GeneratePlan", {
            "persona": persona,
            "query": data.query,
        }),
        handle_res
    )
    
    # FIX: ENDを送るのがStreamerよりも早すぎるせいで最後の一文字が送られない
    await manager.send_end()


@WsManager.websocket("/chat", QueryTableSchema)
async def _(data: QueryTableSchema, manager: WebSocketManager):
    # ユーザーIDの取得（将来的にはWebSocketのヘッダーから取得）
    data.user_id = get_default_user_id()

    archive = http_client.post(
        "http://archive-service:8000/api/v1/archive",
        {
            "query_id": str(data.id),
            "archive_type": "CHAT",
            "contents": {
                "message": ""
            }
        }
    )

    print(data, flush=True)

    # LLMで推論
    message = ""
    async def handle_res(res):
        nonlocal message
        message += res
        await manager.send_data({
            "contents": {
                "message": message
            }
        })
    await streamer(
        lambda: gRPC_Client("Chat").call_server_stream("ChatInvoke", {
            "query": data.query,
        }),
        handle_res
    )

    # DBを更新
    http_client.put(
        "http://archive-service:8000/api/v1/archive",
        {
            "id": archive["id"],
            "contents": {
                "message": message
            }
        }
    )

    await manager.send_end(None)
