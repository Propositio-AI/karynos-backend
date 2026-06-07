from typing import Any

from app.gateways.db.base_prisma_gateway import BasePrismaGateway
from app.gateways.result import GatewayResult
from app.gen.prisma import types as prisma_types
from app.gen.prisma.models import Conversation, ConversationParticipant, Message


class ChatGateway(BasePrismaGateway):
    CONVERSATION = "conversation"
    PARTICIPANT = "conversationparticipant"
    MESSAGE = "message"

    def create_conversation(
        self,
        payload: prisma_types.ConversationCreateInput | dict[str, Any],
    ) -> GatewayResult[Conversation]:
        return self.create(self.CONVERSATION, payload)

    def create_conversation_participant(
        self,
        payload: prisma_types.ConversationParticipantCreateInput | dict[str, Any],
    ) -> GatewayResult[ConversationParticipant]:
        return self.create(self.PARTICIPANT, payload)

    def read(self, filters: list[list[Any]]) -> GatewayResult[list[Message]]:
        where: dict[str, Any] = {}
        for column, _, value in filters:
            where[column] = value
        return self.find_many(self.MESSAGE, where, order={"created_at": "asc"})

    def list_conversations_by_owner(self, owner_id: str) -> GatewayResult[list[Conversation]]:
        return self.find_many(self.CONVERSATION, {"owner_id": str(owner_id)}, order={"created_at": "asc"})

    def get_conversation(self, conversation_id: str) -> GatewayResult[list[Conversation]]:
        return self.find_many(self.CONVERSATION, {"conversation_id": str(conversation_id)})

    def update_conversation(
        self,
        conversation_id: str,
        update_data: prisma_types.ConversationUpdateInput | dict[str, Any],
    ) -> GatewayResult[list[Conversation]]:
        return self.update_many_and_fetch(self.CONVERSATION, {"conversation_id": str(conversation_id)}, update_data)

    def delete_conversation(self, conversation_id: str) -> GatewayResult[list[Conversation]]:
        return self.delete_many_and_return_before(self.CONVERSATION, {"conversation_id": str(conversation_id)})

    def delete_conversation_participants(self, conversation_id: str) -> GatewayResult[list[ConversationParticipant]]:
        return self.delete_many_and_return_before(self.PARTICIPANT, {"conversation_id": str(conversation_id)})

    def create_message(self, payload: prisma_types.MessageCreateInput | dict[str, Any]) -> GatewayResult[Message]:
        return self.create(self.MESSAGE, payload)

    def list_messages(self, conversation_id: str) -> GatewayResult[list[Message]]:
        return self.find_many(self.MESSAGE, {"conversation_id": str(conversation_id)}, order={"created_at": "asc"})

    def delete_messages_by_conversation(self, conversation_id: str) -> GatewayResult[list[Message]]:
        return self.delete_many_and_return_before(self.MESSAGE, {"conversation_id": str(conversation_id)})

    def delete_message(self, message_id: str) -> GatewayResult[list[Message]]:
        return self.delete_many_and_return_before(self.MESSAGE, {"message_id": str(message_id)})


chat_gateway = ChatGateway()
