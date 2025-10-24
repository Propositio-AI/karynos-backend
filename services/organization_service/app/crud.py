from core.db import session
from shared.lib.crud import CRUD

from models.OrganizationTable import OrganizationTable

organization_crud = CRUD(session, OrganizationTable)