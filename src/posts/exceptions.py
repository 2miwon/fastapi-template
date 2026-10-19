from src.exceptions import NotFound, PermissionDenied


class PostNotFound(NotFound):
    DETAIL = "Post not found"


class PostNotOwned(PermissionDenied):
    DETAIL = "You are not the author of this post"
