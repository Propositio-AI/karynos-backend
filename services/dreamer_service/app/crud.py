from core.db import session
from shared.lib.crud import CRUD

from services.job_service.app.models.DreamerGroupMembersTable import DreamerGroupMembersTable
from services.job_service.app.models.DreamerGroupTable import DreamerGroupTable
from services.job_service.app.models.DreamerTable import DreamerTable


dreamer_group_members_crud = CRUD(session, DreamerGroupMembersTable)
dreamer_group_crud = CRUD(session, DreamerGroupTable)
dreamer_crud = CRUD(session, DreamerTable)
