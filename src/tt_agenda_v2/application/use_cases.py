from tt_agenda_v2.application.ports import UserRepository
from tt_agenda_v2.domain import User


def authenticate_user(
    user_repository: UserRepository,
    username: str,
    password: str,
) -> User | None:
    user = user_repository.get_by_username(username)
    if user is None:
        return None
    if not user.check_password(password):
        return None
    return user
