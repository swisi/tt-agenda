from typing import Protocol

from tt_agenda_v2.domain import User


class UserRepository(Protocol):
    def get_by_username(self, username: str) -> User | None:
        ...
