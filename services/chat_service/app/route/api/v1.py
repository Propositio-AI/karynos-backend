from fastapi import HTTPException, APIRouter, Depends
from fastapi.responses import StreamingResponse
from uuid import UUID

from shared.lib.basicError import errorWrapper, BasicError
from shared.lib.auth import get_current_user_id, get_current_user_id_str
from crud import conversation_participants_crud,conversation_table_crud,messages_crud
from services.external.job_api import get_job_data
from services.character_service import generate_name
from services.chat_context import build_openai_messages
from repositories.message_repository import get_messages_db
from schemas import CreateConversationRequest, CreateConversationDB, NewMessageRequest, NewUserMessageDB, NewAIMessageDB
from LLM_Client.OpenAI import OpenAIClient
# /api/v1/chat
router = APIRouter()

ASSISTANT_SENDER_ID = "22222222-2222-2222-2222-222222222222"

# ====================
# 会話作成
# ====================
@router.post("/")
async def create_new_conversation(
    request: CreateConversationRequest,
    user_id: UUID = Depends(get_current_user_id)
):
    """新しい会話を作成"""
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
    response = conversation_table_crud.create(new_conversation_db)
    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])
    return response["data"]

# ====================
# 会話履歴を取得
# ====================
@router.get("/history")
async def get_conversation_history(
    user_id: str = Depends(get_current_user_id_str)
):
    """会話履歴を取得"""
    response = conversation_table_crud.read([
        ["owner_id", "==", user_id]
    ])
    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])
    return response["data"]


# ====================
# 会話情報を取得
# ====================
@router.get("/conversation/{conversation_id}")
async def get_conversation_details(conversation_id: str):    
    response = conversation_table_crud.read([
        ["conversation_id", "==", conversation_id]
    ])
    if not response["success"] or not response["data"]:
        raise HTTPException(status_code=404, detail=response["message"])
    
    conversation = response["data"][0]

    messages = get_messages_db(
        conversation_id=conversation_id,
        crud=messages_crud
    )

    return {
        "conversation": conversation, 
        "messages": messages
    }

# @router.get("/conversation/{conversation_id}")
# async def get_conversation_details(conversation_id: str):
#     """会話の詳細を取得"""
#     conversation = get_messages_db(
#         conversation_id = conversation_id,
#         crud = messages_crud
#     )
#     return conversation

@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """会話を削除"""
    # 会話参加者の削除
    delete_participants_response = conversation_participants_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    if not delete_participants_response["success"]:
        raise HTTPException(status_code=500, detail=delete_participants_response["message"])
    # メッセージの削除
    delete_messages_response = messages_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    if not delete_messages_response["success"]:
        raise HTTPException(status_code=500, detail=delete_messages_response["message"])
    # 会話自体の削除
    delete_conversation_response = conversation_table_crud.delete([
        ["conversation_id", "==", conversation_id]
    ])
    if not delete_conversation_response["success"]:
        raise HTTPException(status_code=500, detail=delete_conversation_response["message"])
    return {"message": "Conversation deleted successfully"}

@router.post("/message/{conversation_id}")
async def create_new_ai_response(
    conversation_id: str,
    request: NewMessageRequest,
    user_id: str = Depends(get_current_user_id_str)
):
    """新しいAI応答メッセージを作成"""
    user_message = NewUserMessageDB(
        conversation_id = conversation_id,
        sender_id = user_id,
        role = request.role,
        text_content = request.text_content
    )

    response = messages_crud.create(user_message)
    
    if not response["success"]:
        raise HTTPException(status_code=500, detail=response["message"])
    
    update_response = conversation_table_crud.update(
        filters = [["conversation_id", "==", conversation_id]],
        update_data = {"last_message_at": response["data"].created_at}
    )
    
    if not update_response["success"]:
        raise HTTPException(status_code=500, detail=update_response["message"])

    conversation_response = conversation_table_crud.read([
        ["conversation_id", "==", conversation_id]
    ])
    
    if not conversation_response["success"]:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversation_response["data"][0]
    
    openai_messages = build_openai_messages(
        conversation_id = conversation_id, 
        job_id = conversation.job_id, 
        messages_crud = messages_crud, 
        system_prompt_path = "prompts/character_prompt.txt"
    )

    openai_client = OpenAIClient()
    async def stream_ai_response():
        ai_message_content = ""
        try:
            async for chunk in openai_client.chat_stream(openai_messages):
                ai_message_content += chunk
                yield chunk
        except Exception as e:
            print(e, flush=True)
        finally:
            if ai_message_content:
                # ストリーミング終了後にメッセージをDBに保存
                ai_message = NewAIMessageDB(
                    conversation_id = conversation_id,
                    sender_id = ASSISTANT_SENDER_ID,
                    role = "assistant",
                    text_content = ai_message_content
                )
                ai_response = messages_crud.create(ai_message)
                if not ai_response["success"]:
                    print(ai_response["message"], flush=True)
            return

    return StreamingResponse(stream_ai_response(), media_type="text/event-stream")

@router.delete("/message/{message_id}")
async def delete_messages_in_conversation(message_id: str):
    """会話内のメッセージを削除"""
    delete_response = messages_crud.delete([
        ["message_id", "==", message_id]
    ])
    if not delete_response["success"]:
        raise HTTPException(status_code=500, detail=delete_response["message"])
    return {"message": "Message deleted successfully"}