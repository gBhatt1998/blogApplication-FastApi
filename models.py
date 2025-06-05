from pydantic import EmailStr, Field
from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, index=True)
    username=Column(String(50),unique=True)
    email = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=True) 
   


class Post(Base):
    __tablename__="posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50))
    content = Column(String(100))
    user_id = Column(Integer)