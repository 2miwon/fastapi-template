from src.exceptions import BadRequest, Conflict, NotAuthenticated


class InvalidCredentials(NotAuthenticated):
    DETAIL = "Invalid email or password"


class InvalidToken(NotAuthenticated):
    DETAIL = "Invalid or expired token"


class EmailTaken(Conflict):
    DETAIL = "Email is already taken"


class InactiveUser(BadRequest):
    DETAIL = "Inactive user"
