from tt_agenda_v2.domain import User


class InMemoryUserRepository:
    def __init__(self, users: list[User]) -> None:
        self._users = {user.username: user for user in users}

    @classmethod
    def create_with_defaults(
        cls,
        admin_username: str,
        admin_password: str,
        user_username: str,
        user_password: str,
    ) -> "InMemoryUserRepository":
        return cls(
            users=[
                User(username=admin_username, password=admin_password, role="admin"),
                User(username=user_username, password=user_password, role="user"),
            ]
        )

    def get_by_username(self, username: str) -> User | None:
        return self._users.get(username)
