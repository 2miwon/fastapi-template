import uuid
from datetime import datetime

from pydantic import Field

from src.posts.constants import TITLE_MAX_LENGTH
from src.schemas import CustomModel


class PostCreate(CustomModel):
    title: str = Field(min_length=1, max_length=TITLE_MAX_LENGTH)
    content: str = ""


class PostUpdate(CustomModel):
    title: str | None = Field(default=None, min_length=1, max_length=TITLE_MAX_LENGTH)
    content: str | None = None


class PostResponse(CustomModel):
    id: uuid.UUID
    author_id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime | None
