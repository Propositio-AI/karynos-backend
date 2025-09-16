from models.ArchiveTable import ArchiveTable
from core.db import session
from shared.lib.crud import CRUD

archive_crud = CRUD(session, ArchiveTable)
