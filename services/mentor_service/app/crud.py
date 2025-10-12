from core.db import session
from shared.lib.crud import CRUD

from services.job_service.app.models.MetnorsTable import MetnorsTable
from services.job_service.app.models.MentorGroupsTable import MentorGroupsTable
from services.job_service.app.models.MentorGroupMembersTable import MentorGroupMembersTable

mentors_crud = CRUD(session, MetnorsTable)
mentor_groups_crud = CRUD(session, MentorGroupsTable)
mentor_group_members_crud = CRUD(session, MentorGroupMembersTable)
