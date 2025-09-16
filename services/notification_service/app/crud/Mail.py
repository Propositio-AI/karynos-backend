from models.MailTable import MailTable
from core.db import session
from shared.lib.crud import CRUD

mail_crud = CRUD(session, MailTable)
