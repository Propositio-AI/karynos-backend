from fastapi import APIRouter

from models.QueryTable import QueryTableSchema

from crud.Query import query_crud
from shared.lib.api_client import HTTP_APIClient
from shared.lib.gRPC.client import gRPC_Client
from shared.lib.websocket import WebSocketManager, streamer

# /ws/v1/query
router = APIRouter()

http_client = HTTP_APIClient()

@WebSocketManager(router, "/plan", QueryTableSchema).websocket()
async def _(data: QueryTableSchema, manager: WebSocketManager):

    # TODO: ユーザーID取得処理
    data.user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    # 新規クエリーをクエリーDBに保存
    query = query_crud.create(data)

    # 学習プランの保存用のレコードを作成
    plan_archive = http_client.post(
        url = "http://archive-service:8000/archive",
        data = {
            "query_id": str(query.id),
            "archive_type": 'PLAN',
            "contents": {"notions" : []}
        }
    )

    # LLMで学習プランを作成
    notions = ""
    async def handle_res(res):
        nonlocal notions
        notions += res
        await manager.send_update(
            id=str(plan_archive["id"]),
            update={"contents": {"notions": notions.split("\n")}},
        )

    await streamer(
        lambda: gRPC_Client("TextBook").call_server_stream("GeneratePlan", {
            "query": data.query,
            "query_id": str(query.id)
        }),
        handle_res
    )
    
    # ENDを送るのがStreamerよりも早すぎるせいで最後の一文字が送られない
    await manager.send_end(
        plan_archive["id"],
        {"query_id": str(query.id)}
    )


    # notions = notions.split("\n")
    # # 学習プランをアーカイブDBに保存
    # http_client.post(
    #     url = "http://archive-service:8000/archive",
    #     data = {
    #         "query_id": str(query.id),
    #         "archive_type": 'PLAN',
    #         "contents": {"notions" : notions}
    #     }
    # )


# @router.websocket("/chat")
# async def _(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             data = json.loads(data)

#            # TODO: ユーザーID取得処理
#             data.user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"

#             # 新規クエリーをクエリーDBに保存
#             # query = query_crud.create(data)

#             llm_client = gRPC_Client("LLM")
#             for res in llm_client.call_server_stream("ChatInvoke", {
#                 "query": data.query,
#                 "query_id": ""
#             }):
#                 await websocket.send_text(res)

#             # TODO: DBに保存する機能
            
#             # # LLMで学習プランを作成
#             # ai_message = gRPC_Client("LLM").call("ChatInvoke", {
#             #     "query": data.query,
#             #     "query_id": str(query.id)
#             # })

#             # client.post(
#             #     url = "http://archive-service:8000/archive",
#             #     data = {
#             #         "query_id": str(query.id),
#             #         "archive_type": 'CHAT',
#             #         "contents": {"message": ai_message["response"]}
#             #     }
#             # )

#             # return query
#     except Exception as e:
#         print(e)