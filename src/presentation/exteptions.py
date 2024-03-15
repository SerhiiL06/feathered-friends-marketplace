from dataclasses import dataclass


@dataclass
class PasswordError:
    code: int
    message: str
