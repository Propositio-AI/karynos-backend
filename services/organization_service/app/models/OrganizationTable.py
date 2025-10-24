from sqlalchemy.schema import Column
from sqlalchemy.types import (
    INTEGER,
    TEXT,
    DateTime
)
from sqlalchemy import func
from pydantic import BaseModel
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum

from shared.utils.shema import sqlalchemy_to_pydantic
from models.base import Base

class OrganizationType(PyEnum):
    SCHOOL_ELEMENTARY = "SCHOOL_ELEMENTARY"
    SCHOOL_JUNIOR = "SCHOOL_JUNIOR"
    SCHOOL_HIGH = "SCHOOL_HIGH"
    COMPANY = "COMPANY"
    OTHER = "OTHER"

class OrganizationTable(Base):
    __tablename__ = "organization"

    organization_id = Column(INTEGER, primary_key=True)
    organization_name = Column(TEXT, nullable=False)
    display_name = Column(TEXT, nullable=False)
    organization_type = Column(SQLEnum(OrganizationType, name="organization_type", create_type=False), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


OrganizationTableSchema: BaseModel = sqlalchemy_to_pydantic(OrganizationTable)