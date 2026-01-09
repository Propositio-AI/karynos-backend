from fastapi import Depends, HTTPException, APIRouter
from fastapi.responses import StreamingResponse

from shared.lib.API.auth.main import get_current_user
from shared.lib.basicError import errorWrapper, BasicError
from crud import conversation_participants_crud,conversation_table_crud,messages_crud
from services.external.job_api import get_job_data
from services.character_service import generate_name
from services.chat_context import build_openai_messages
from repositories.message_repository import get_messages_db
from schemas import CreateConversationRequest, CreateConversationDB, NewMessageRequest, NewUserMessageDB, NewAIMessageDB
from LLM_Client.OpenAI import OpenAIClient
# /api/v1/chat
router = APIRouter()

@router.post("/")
async def create_new_conversation(request: CreateConversationRequest, user = Depends(get_current_user)):
    """新しい会話を作成"""
    user_id = user["dreamer_id"]

    job_data = get_job_data(request.job_id)
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    new_conversation_db = CreateConversationDB(
        owner_id = user_id,
        job_id = request.job_id,
        job_name = job_data['name'],
        assistant_gender = "unisex",
        assistant_name = generate_name(name_type=["japanese_surnames", "japanese_unisex_names"])
    )
    conversation = conversation_table_crud.create(new_conversation_db)

    return conversation

@router.get("/history/{user_id}")
async def get_conversation_history(user_id: str):
    """会話履歴を取得"""
    success, conversations, err = conversation_table_crud.read([
        ["owner_id", "==", user_id]
    ])
    if not success:
        raise HTTPException(status_code=500, detail=err)
    return conversations

# ... (import部分はそのまま)

# ★修正: 会話情報とメッセージの両方を返すように変更
@router.get("/conversation/{conversation_id}")
async def get_conversation_details(conversation_id: str, user = Depends(get_current_user)):
    """会話の詳細（メタデータ＋メッセージ履歴）を取得"""
    
    # 1. 会話データ（job_nameなどが含まれる）を取得
    # curd.read はリストを返すので [0] を取得
    success, conv_data, err = conversation_table_crud.read([
        ["conversation_id", "==", conversation_id],
        ["owner_id", "==", user["id"]]
    ])
    if not success or not conv_data:
        raise HTTPException(status_code=404, detail=err)
    
    conversation = conv_data[0]

    # 2. メッセージ履歴を取得
    messages = get_messages_db(
        conversation_id=conversation_id,
        crud=messages_crud
    )

    # 3. セットにして返す
    return {
        "conversation": conversation,
        "messages": messages
    }

@router.get("/conversation/{conversation_id}")
async def get_conversation_details(conversation_id: str, user = Depends(get_current_user)):
    """会話の詳細を取得"""

    conversation = get_messages_db(
        conversation_id = conversation_id,
        crud = messages_crud
    )
    return conversation

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """会話を削除"""
    # 会話参加者の削除
    conversation_participants_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    # メッセージの削除
    messages_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    # 会話自体の削除
    conversation_table_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    return {"message": "Conversation deleted successfully"}

@router.post("/message/{conversation_id}")
async def create_new_ai_response(conversation_id: str, request: NewMessageRequest, user = Depends(get_current_user)):
    """新しいAI応答メッセージを作成"""

    
    user_message = NewUserMessageDB(
        conversation_id = conversation_id,
        sender_id = user["id"],
        role = request.role,
        text_content = request.text_content
    )
    success, result, err = messages_crud.create(user_message)
    if not success:
        raise HTTPException(status_code=500, detail=err)
    conversation_table_crud.update(
        filters = [["conversation_id", "==", conversation_id]],
        update_data = {"last_message_at": result.created_at}
    )

    success,conversation_data, err = conversation_table_crud.read([
        ["conversation_id", "==", conversation_id],
        ["owner_id", "==", user["id"]]
    ])
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversation = conversation_data[0]
    print(conversation, flush=True)
    openai_messages = build_openai_messages(
        conversation_id = conversation_id, 
        job_id = conversation.job_id, 
        messages_crud = messages_crud, 
        system_prompt_path = "prompts/character_prompt.txt"
        )

    openai_client = OpenAIClient()
    async def stream_ai_response():
        ai_message_content = ""
        async for chunk in openai_client.chat_stream(openai_messages):
            ai_message_content += chunk
            yield chunk
        # ストリーミング終了後にメッセージをDBに保存
        ai_message = NewAIMessageDB(
            conversation_id = conversation_id,
            role = "assistant",
            text_content = ai_message_content
        )
        messages_crud.create(ai_message)

    return StreamingResponse(stream_ai_response(), media_type="text/event-stream")

@router.delete("/message/{message_id}")
async def delete_messages_in_conversation(message_id: str):
    """会話内のメッセージを削除"""
    messages_crud.delete([
        ["message_id", "==", message_id]
    ])
    return {"message": "Message deleted successfully"}