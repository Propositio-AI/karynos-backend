# Routing file

from fastapi import APIRouter
from schemas.UserSchema import newUserModel

router = APIRouter()

@router.post("/")
async def newUser(data: newUserModel):
    pass

@router.get("/")
async def newUser():
    pass

@router.put("/")
async def newUser():
    pass