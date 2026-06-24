from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.lib.auth import get_current_user_id, get_current_user_id_str
from app.schemas.chats import CreateConversationRequest, NewMessageRequest
from app.services.chat.conversation import conversation_service

router = APIRouter()


@router.post("/")
async def create_new_conversation(
    request: CreateConversationRequest,
    user_id: UUID = Depends(get_current_user_id),
):
    return await conversation_service.create_conversation(request, user_id)


@router.get("/history")
async def get_conversation_history(
    user_id: str = Depends(get_current_user_id_str),
):
    return conversation_service.list_conversation_history(user_id)


@router.get("/conversation/{conversation_id}")
async def get_conversation_details(conversation_id: str):
    return conversation_service.get_conversation_details(conversation_id)


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    return conversation_service.delete_conversation(conversation_id)


@router.post("/message/{conversation_id}")
async def create_new_ai_response(
    conversation_id: str,
    request: NewMessageRequest,
    user_id: str = Depends(get_current_user_id_str),
):
    return StreamingResponse(
        conversation_service.create_ai_response_stream(
            conversation_id=conversation_id,
            request=request,
            user_id=user_id,
        ),
        media_type="text/event-stream",
    )


@router.delete("/message/{message_id}")
async def delete_messages_in_conversation(message_id: str):
    return conversation_service.delete_message(message_id)
