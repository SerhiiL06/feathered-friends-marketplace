from dataclasses import dataclass
from pydantic import EmailStr


@dataclass
class AddressDTO:
    name: str
    city: str
    street: str


@dataclass
class LoginDTO:
    email: EmailStr
    password: str


@dataclass
class RegisterDTO:
    email: EmailStr
    password1: str
    password2: str


@dataclass
class UserDTO(RegisterDTO):
    address: AddressDTO = None
    gender: str = None
