# User Table

from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, TEXT, UUID, INTEGER
from sqlalchemy import func
from pydantic import BaseModel

from shared.utils.time import get_utc_time
from shared.utils.security import gen_uuid7
from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class UserTable(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid7)
    last_name = Column(TEXT)
    first_name = Column(TEXT)
    email = Column(TEXT)
    user_type = Column(INTEGER)
    grade = Column(INTEGER)
    class_no = Column(INTEGER)
    student_no = Column(INTEGER)
    school = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime)

UserTableSchema: BaseModel = sqlalchemy_to_pydantic(UserTable)
