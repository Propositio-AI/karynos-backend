# Create Sample DB Data

from core.db import session
from schemas.UserSchema import UserTableSchema
from schemas.UserTypeSchema import UserTypeTableSchema
from crud.UserType import create_user_type
from crud.User import create_user

def init_user_type():
    # User Type
    user_types = [
        UserTypeTableSchema(type="general"),
        UserTypeTableSchema(type="student"),
        UserTypeTableSchema(type="teacher"),
        UserTypeTableSchema(type="admin"),
    ]

    for user_type in user_types:
        create_user_type(
            db=session,
            data=user_type
        )

def init_user():
    # User
    sampleUsers = [
        UserTableSchema(first_name="Toya", email="toya@propositio.com"),
        UserTableSchema(first_name="Ren", email="ren@propositio.com"),
        UserTableSchema(first_name="Kage", email="kage@propositio.com"),
    ]

    for user in sampleUsers:
        try:
            create_user(
                db=session,
                data=user
            )
        except:
            pass