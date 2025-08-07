# Create SQLAlchemy Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.AuthTable import AuthTable
from models.RefreshTable import RefreshTable
from core.config import settings
from models.base import Base

engine = create_engine(settings.db_url)
Base.metadata.create_all(engine)
SessionClass = sessionmaker(engine)
session = SessionClass()