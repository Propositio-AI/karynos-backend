from core.db import session
from shared.lib.crud import CRUD

from models.MentorsTable import MentorsTable
from models.MentorGroupsTable import MentorGroupsTable
from models.MentorGroupMembersTable import MentorGroupMembersTable

mentors_crud = CRUD(session, MentorsTable)
mentor_groups_crud = CRUD(session, MentorGroupsTable)
mentor_group_members_crud = CRUD(session, MentorGroupMembersTable)
