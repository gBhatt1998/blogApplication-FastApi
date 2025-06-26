
from sqlalchemy import Column, Integer, String, Enum
from core.database import Base
import enum

class Role(str, enum.Enum):
    USER = "user"
    WRITER = "writer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=True)
    role = Column(Enum(Role), default=Role.USER, nullable=False)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)
