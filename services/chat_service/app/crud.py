from core.db import session
from shared.lib.crud import CRUD

from models.ConversationParticipantsTable import ConversationParticipantsTable
from models.ConversationsTable import ConversationsTable
from models.MessagesTable import MessagesTable


conversation_participants_crud = CRUD(session, ConversationParticipantsTable)
conversation_table_crud = CRUD(session, ConversationsTable)
messages_crud = CRUD(session, MessagesTable)
