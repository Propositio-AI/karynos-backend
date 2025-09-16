from models.RefreshTable import RefreshTable
from core.db import session
from shared.lib.crud import CRUD

refresh_crud = CRUD(session, RefreshTable)
