# Routing file

from fastapi import APIRouter
from schemas.MailSchema import newMailModel

from endpoints.mail import sendMail

router = APIRouter()

@router.post("/mail/send")
async def newMail(data: newMailModel):
    sendMail()

