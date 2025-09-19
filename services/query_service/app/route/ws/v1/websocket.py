from fastapi import APIRouter
from pydantic import BaseModel

from models.QueryTable import QueryTableSchema

from shared.lib.api_client import HTTP_APIClient
from shared.lib.gRPC.client import gRPC_Client
from shared.lib.websocket import WebSocketManager, streamer


# /ws/v1/query
router = APIRouter()
WsManager = WebSocketManager(router)

http_client = HTTP_APIClient()

class PlanQuerySchema(BaseModel):
    query: str
@WsManager.websocket("/plan", PlanQuerySchema)
async def _(data: PlanQuerySchema, manager: WebSocketManager):
    # TODO: ユーザーID取得処理 
    # ユーザーIDはDBに保存しないためこのタイミングでは必要ないが、ログとして残すなら必要になる
    # data.user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

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
            "query": data.query,
        }),
        handle_res
    )
    
    # FIX: ENDを送るのがStreamerよりも早すぎるせいで最後の一文字が送られない
    await manager.send_end()


@WsManager.websocket("/chat", QueryTableSchema)
async def _(data: QueryTableSchema, manager: WebSocketManager):

    # TODO: ユーザーID取得処理
    data.user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    # 新規クエリーをクエリーDBに保存
    # ユーザー側で実行
    # query = query_crud.create(data)

    # チャットの保存用のレコードを作成
    chat_archive = http_client.post(
        url = "http://archive-service:8000/api/v1/archive",
        data = {
            "query_id": str(data.id),
            "archive_type": 'CHAT',
            "contents": {"message" : ""}
        }
    )

    # archiveデータを送信
    manager.send_start({
        "id": str(chat_archive["id"])
    })

    # LLMで学習プランを作成
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
    
    # FIX: ENDを送るのがStreamerよりも早すぎるせいで最後の一文字が送られない
    await manager.send_end({
        "id": chat_archive["id"]
    })

    #TODO: DBに保存する
    # status: SUCCEEDED