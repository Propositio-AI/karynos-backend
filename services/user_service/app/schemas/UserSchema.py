import uuid
from datetime import datetime
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: uuid.UUID= None
    name: str= None
    email: str= None
    user_type: uuid.UUID= None
    grade: int= None
    class_no: int= None
    student_no: int= None
    school: uuid.UUID= None
    created_at: datetime = None
    updated_at: datetime = None
    last_login_at: datetime = None

class newUserModel(BaseModel):
    name: str= None
    email: str= None
    user_type: uuid.UUID= None
    class_info: uuid.UUID= None
    school: uuid.UUID= None
