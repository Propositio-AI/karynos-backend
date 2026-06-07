from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import HTTPException

from app.services.chat_service.LLM_Client.OpenAI import OpenAIClient
from app.gateways import chat_gateway
from app.schemas.chats import (
    CreateConversationDB,
    CreateConversationRequest,
    NewAIMessageDB,
    NewMessageRequest,
    NewUserMessageDB,
)
from app.services.chat_service.services.character_service import generate_name
from app.services.chat_service.services.chat_context import build_openai_messages
from app.services.chat_service.services.external.job_api import get_job_data, normalize_job_id

ASSISTANT_SENDER_ID = "22222222-2222-2222-2222-222222222222"


class ConversationService:
    async def create_conversation(self, request: CreateConversationRequest, user_id: UUID):
        normalized_job_id = normalize_job_id(request.job_id)
        job_data = await get_job_data(normalized_job_id)
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        new_conversation = CreateConversationDB(
            owner_id=user_id,
            job_id=normalized_job_id,
            job_name=job_data["name"],
            assistant_gender="unisex",
            assistant_name=generate_name(
                name_type=["japanese_surnames", "japanese_unisex_names"]
            ),
        )
        response = chat_gateway.create_conversation(new_conversation)
        self._ensure_success(response)
        conversation = response["data"]

        participant_response = chat_gateway.create_conversation_participant(
            {
                "conversation_id": str(conversation.conversation_id),
                "user_id": str(user_id),
            }
        )
        self._ensure_success(participant_response)
        return conversation

    def list_conversation_history(self, user_id: str):
        response = chat_gateway.list_conversations_by_owner(user_id)
        self._ensure_success(response)
        return response["data"]

    def get_conversation_details(self, conversation_id: str):
        conversation_response = chat_gateway.get_conversation(conversation_id)
        if not conversation_response["success"] or not conversation_response["data"]:
            raise HTTPException(
                status_code=404,
                detail=self._detail_from_message(conversation_response, "Conversation not found"),
            )

        messages_response = chat_gateway.list_messages(conversation_id)
        self._ensure_success(messages_response)
        return {
            "conversation": conversation_response["data"][0],
            "messages": messages_response["data"],
        }

    def delete_conversation(self, conversation_id: str):
        participants_response = chat_gateway.delete_conversation_participants(conversation_id)
        self._ensure_success(participants_response)

        messages_response = chat_gateway.delete_messages_by_conversation(conversation_id)
        self._ensure_success(messages_response)

        conversation_response = chat_gateway.delete_conversation(conversation_id)
        self._ensure_success(conversation_response)
        return {"message": "Conversation deleted successfully"}

    async def create_ai_response_stream(
        self,
        conversation_id: str,
        request: NewMessageRequest,
        user_id: str,
    ) -> AsyncIterator[str]:
        user_message = NewUserMessageDB(
            conversation_id=conversation_id,
            sender_id=user_id,
            role=request.role,
            text_content=request.text_content,
        )
        create_message_response = chat_gateway.create_message(user_message)
        if not create_message_response["success"]:
            detail = self._detail_from_message(create_message_response, "Failed to create message")
            yield f"event: error\ndata: {detail}\n\n"
            return

        update_response = chat_gateway.update_conversation(
            conversation_id,
            {"last_message_at": create_message_response["data"].created_at},
        )
        if not update_response["success"]:
            detail = self._detail_from_message(update_response, "Failed to update conversation")
            yield f"event: error\ndata: {detail}\n\n"
            return

        conversation_response = chat_gateway.get_conversation(conversation_id)
        if not conversation_response["success"] or not conversation_response["data"]:
            yield "event: error\ndata: Conversation not found\n\n"
            return

        conversation = conversation_response["data"][0]
        openai_messages = await build_openai_messages(
            conversation_id=conversation_id,
            job_id=conversation.job_id,
            messages_crud=chat_gateway,
        )

        openai_client = OpenAIClient()
        ai_message_content = ""
        try:
            async for chunk in openai_client.chat_stream(openai_messages):
                ai_message_content += chunk
                yield chunk
        except Exception as exc:
            print(exc, flush=True)
        finally:
            if ai_message_content:
                ai_message = NewAIMessageDB(
                    conversation_id=conversation_id,
                    sender_id=ASSISTANT_SENDER_ID,
                    role="assistant",
                    text_content=ai_message_content,
                )
                ai_response = chat_gateway.create_message(ai_message)
                if not ai_response["success"]:
                    print(self._detail_from_message(ai_response, "Failed to save ai response"), flush=True)

    def delete_message(self, message_id: str):
        response = chat_gateway.delete_message(message_id)
        self._ensure_success(response)
        return {"message": "Message deleted successfully"}

    def _ensure_success(self, response: dict):
        if response["success"]:
            return
        raise HTTPException(
            status_code=500,
            detail=self._detail_from_message(response, "Unexpected gateway failure"),
        )

    def _detail_from_message(self, response: dict, fallback: str):
        message = response.get("message", fallback)
        if isinstance(message, list):
            return ", ".join(message)
        return message


conversation_service = ConversationService()