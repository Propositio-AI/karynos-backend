# Create Sample DB Data

from core.db import session
from schemas.UserTypeSchema import UserTypeSchema
from crud.UserType import create_user_type

# User Type
user_types = [
    UserTypeSchema(type="general"),
    UserTypeSchema(type="student"),
    UserTypeSchema(type="teacher"),
    UserTypeSchema(type="admin"),
]

for user_type in user_types:
    create_user_type(
        db=session,
        data=user_type
    )