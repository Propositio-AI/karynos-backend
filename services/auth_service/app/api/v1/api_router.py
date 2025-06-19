# Routing file

from fastapi import APIRouter
from schemas.AuthSchema import MailModel
from api.v1.endpoints.magic_link import SendMail
from api.v1.endpoints.vertify import Vertify

router = APIRouter()

# Sending mail
@router.post("/send")
async def send(data: MailModel):    
    send_mail = SendMail(data.email)
    db_response = send_mail.add_token()
    send_mail.send()

    return {
            "email": db_response.email,
            "created_at": db_response.created_at,
            "expires_at": db_response.expires_at
           }


# Vertify
@router.get("/vertify")
async def vertify(token:str):
    vertify = Vertify(token)
    valid_token =vertify.vertify_token()

    print(valid_token)