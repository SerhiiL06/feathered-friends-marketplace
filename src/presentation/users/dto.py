from dataclasses import dataclass
from enum import Enum

from pydantic import EmailStr


class RoleEnum(Enum):
    client = 1
    manager = 2
    admin = 3


@dataclass
class AddressDTO:
    name: str
    city: str
    street: str


@dataclass
class RegisterDTO:
    email: EmailStr
    first_name: str
    last_name: str
    city: str
    password1: str
    password2: str


@dataclass
class UserDTO:
    email: EmailStr
    first_name: str
    last_name: str
    city: str
    address: AddressDTO = None
    gender: str = None
