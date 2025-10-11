from models.MemoTable import MemoTable
from core.db import session
from shared.lib.crud.crud import CRUD

memo_crud = CRUD(session, MemoTable)
