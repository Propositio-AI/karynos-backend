from models.AuthTable import AuthTable
from core.db import session
from shared.lib.crud.crud import CRUD

auth_crud = CRUD(session, AuthTable)
