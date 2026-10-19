"""Import every domain's models so `Base.metadata` is complete (used by Alembic)."""

from src.auth.models import User
from src.database import Base
from src.posts.models import Post

__all__ = ["Base", "Post", "User"]
