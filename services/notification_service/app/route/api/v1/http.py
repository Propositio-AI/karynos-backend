# Routing file

from fastapi import APIRouter
from models.MailTable import MailTableSchema

# /api/v1/notification
router = APIRouter()

@router.post("/mail/send")
async def newMail(data: MailTableSchema):
    pass

