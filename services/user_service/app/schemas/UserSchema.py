import uuid
from datetime import datetime
from pydantic import BaseModel

# TODO:set default value 
class UserTableSchema(BaseModel):
    id: uuid.UUID= None
    last_name: str= None
    first_name: str
    email: str
    user_type:int = 1  
    grade: int= None
    class_no: int= None
    student_no: int= None
    school: uuid.UUID= None
    created_at: datetime = None
    updated_at: datetime = None
    last_login_at: datetime = None

class newUserSchema(BaseModel):
    last_name: str= None
    first_name: str = None
    email: str
    user_type:int = 1  
    grade: int= None
    class_no: int= None
    student_no: int= None
    school: uuid.UUID= None
