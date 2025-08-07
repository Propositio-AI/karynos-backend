import requests

from schemas.QuerySchema import newQuerySchema
from schemas.QuerySchema import QueryTableSchema
from crud.Query import create_query
from shared.lib.api_client import HTTP_APIClient

def add_query(data: newQuerySchema):
    # TODO : ユーザーIDを取得する処理

    # TODO: このクライアントクラスにユーザーの持っているトークンを紐づけさせる
    client = HTTP_APIClient()

    if(data.archive_id is None):
        new_archive = client.post(
            url = "http://archive-service:8000/archive",
            data = {
                "type": 1 
            }
        )
        
        archive_id = new_archive["id"]

    #TODO: ユーザーID関連処理
    new_query = create_query(QueryTableSchema(type = data.type, archive_id = archive_id,  user_id = "3fa85f64-5717-4562-b3fc-2c963f66afa6"))

    return {
        "id": new_query.id,
        "archive_id": new_query.archive_id,
        "favorite": new_query.favorite,
        "created_at": new_query.created_at
    }
    