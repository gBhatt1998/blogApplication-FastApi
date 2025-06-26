from pydantic import BaseModel
from typing import Optional

class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int

class PostUpdate(BaseModel):
    title: Optional[str]
    content: Optional[str]
    user_id: Optional[int]
