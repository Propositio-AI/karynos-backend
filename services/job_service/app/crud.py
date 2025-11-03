from core.db import session
from shared.lib.crud import CRUD


from models.HistoryTable import HistoryTable

history_crud = CRUD(session, HistoryTable)
