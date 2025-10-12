from core.db import session
from shared.lib.crud import CRUD

from services.job_service.app.models.JobsTable import JobsTable
from services.job_service.app.models.HistoryTable import HistoryTable
from services.job_service.app.models.ReviewTable import ReviewTable

jobs_crud = CRUD(session, JobsTable)

job_review_crud = CRUD(session, ReviewTable)

history_crud = CRUD(session, HistoryTable)
