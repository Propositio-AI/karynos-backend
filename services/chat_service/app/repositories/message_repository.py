from shared.lib.crud import CRUD

# DBから過去の会話履歴を取得する
def get_messages_db(conversation_id: str, crud: CRUD):
    response = crud.read(
        [
            ["conversation_id", "==", conversation_id]
        ]
    )
    if response["success"]:
        return response["data"]
    raise Exception(f"会話履歴の取得に失敗しました: {', '.join(response['message'])}")
    
"""
実行結果
[
    {
        "conversation_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role":"system",
        "message_id":"2f55ccbc-c52f-40bf-9f38-b79be0dbea7a",
        "created_at":"2025-12-10T04:11:05.535757",
        "text_content":"チャットルームが作成されました。案件について質問してください。",
        "sender_id":"22222222-2222-2222-2222-222222222222",
        "updated_at":"2025-12-10T05:06:05.535757"
    },
    {
        "conversation_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role":"user",
        "message_id":"e6cff558-216a-40d4-aafe-c9d84f51ffe3",
        "created_at":"2025-12-10T04:36:05.535757",
        "text_content":"この案件のリモートワークの頻度について教えてください。",
        "sender_id":"11111111-1111-1111-1111-111111111111",
        "updated_at":"2025-12-10T05:06:05.535757"
    },
    {
        "conversation_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role":"assistant",
        "message_id":"d563bc00-8dcb-4bf4-b64f-e69a3f7fa05e",
        "created_at":"2025-12-10T04:37:05.535757",
        "text_content":"この案件は原則フルリモートですが、月に1回程度の出社が推奨されています。",
        "sender_id":"22222222-2222-2222-2222-222222222222",
        "updated_at":"2025-12-10T05:06:05.535757"
    },
    {
        "conversation_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role":"user",
        "message_id":"885a6b17-bef5-42cf-830d-d0b6567cdacd",
        "created_at":"2025-12-10T05:01:05.535757",
        "text_content":"なるほど、ありがとうございます。年収レンジはどれくらいですか？",
        "sender_id":"11111111-1111-1111-1111-111111111111",
        "updated_at":"2025-12-10T05:06:05.535757"
    },
    {
        "conversation_id":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "role":"assistant",
        "message_id":"4d6508f7-c3f7-4a68-8142-12ee11dc67dd",
        "created_at":"2025-12-10T05:06:05.535757",
        "text_content":"スキル見合いですが、800万〜1200万円のレンジで提示されています。",
        "sender_id":"22222222-2222-2222-2222-222222222222",
        "updated_at":"2025-12-10T05:06:05.535757"
    }
]
"""