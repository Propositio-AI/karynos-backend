from models.QueryTable import QueryTable
from core.db import session
from shared.lib.crud.crud import CRUD

query_crud = CRUD(session, QueryTable)
