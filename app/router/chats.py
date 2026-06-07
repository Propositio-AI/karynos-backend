from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from uuid import UUID

from app.lib.auth import get_current_user_id, get_current_user_id_str
from app.schemas.chats import CreateConversationRequest, NewMessageRequest
from app.services.chat_service.services.conversation_service import conversation_service

router = APIRouter(prefix="/chat")
api_router = APIRouter(prefix="/api/v1")


@api_router.post("/")
async def create_new_conversation(
	request: CreateConversationRequest,
	user_id: UUID = Depends(get_current_user_id),
):
	return await conversation_service.create_conversation(request, user_id)


@api_router.get("/history")
async def get_conversation_history(
	user_id: str = Depends(get_current_user_id_str),
):
	return conversation_service.list_conversation_history(user_id)


@api_router.get("/conversation/{conversation_id}")
async def get_conversation_details(conversation_id: str):
	return conversation_service.get_conversation_details(conversation_id)


@api_router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
	return conversation_service.delete_conversation(conversation_id)


@api_router.post("/message/{conversation_id}")
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


@api_router.delete("/message/{message_id}")
async def delete_messages_in_conversation(message_id: str):
	return conversation_service.delete_message(message_id)


router.include_router(api_router)
