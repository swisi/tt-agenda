from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    password: str
    role: str

    def check_password(self, plain_password: str) -> bool:
        return self.password == plain_password
