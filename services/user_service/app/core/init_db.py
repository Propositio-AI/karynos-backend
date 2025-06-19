# Create Sample DB Data

from core.db import session
from schemas.UserSchema import UserSchema
from schemas.UserTypeSchema import UserTypeSchema
from crud.UserType import create_user_type
from crud.User import create_user

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

# User
sampleUsers = [
    UserSchema(first_name="Toya", email="toya@propositio.com"),
    UserSchema(first_name="Ren", email="ren@propositio.com"),
    UserSchema(first_name="Kage", email="kage@propositio.com"),
]

for user in sampleUsers:
    create_user(
        db=session,
        data=user
    )