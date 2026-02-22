from core.db import session
from shared.lib.crud import CRUD

from models.DreamerGroupMembersTable import DreamerGroupMembersTable
from models.DreamerGroupTable import DreamerGroupTable
from models.DreamerTable import DreamerTable
from models.InitQuestionTable import InitQuestionTable
from models.InitQuestionOptionTable import InitQuestionOptionTable
from models.UserInitialAnswerTable import UserInitialAnswerTable


dreamer_group_members_crud = CRUD(session, DreamerGroupMembersTable)
dreamer_group_crud = CRUD(session, DreamerGroupTable)
dreamer_crud = CRUD(session, DreamerTable)
init_question_crud = CRUD(session, InitQuestionTable)
init_question_option_crud = CRUD(session, InitQuestionOptionTable)
user_initial_answer_crud = CRUD(session, UserInitialAnswerTable)
