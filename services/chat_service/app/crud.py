from core.db import session
from shared.lib.crud import CRUD

from services.job_service.app.models.ConversationParticipantsTable import ConversationParticipantsTable
from services.job_service.app.models.ConversationsTable import ConversationsTable
from services.job_service.app.models.MessagesTable import MessagesTable


conversation_participants_crud = CRUD(session, ConversationParticipantsTable)
conversation_table_crud = CRUD(session, ConversationsTable)
messages_crud = CRUD(session, MessagesTable)
