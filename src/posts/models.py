import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, TimestampMixin
from src.posts.constants import TITLE_MAX_LENGTH


class Post(TimestampMixin, Base):
    __tablename__ = "post"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("auth_user.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    content: Mapped[str] = mapped_column(Text, default="")
