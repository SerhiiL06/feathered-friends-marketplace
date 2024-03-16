from src.repositories.users import UserRepository
from src.presentation.users.mapping import RegisterDTO, LoginDTO
from fastapi import HTTPException, status
from passlib.context import CryptContext


bcrypt = CryptContext(schemes=["bcrypt"])


class UserDomain:
    def __init__(self) -> None:
        self.repo = UserRepository()

    async def register_user(self, data: RegisterDTO):
        errors = self.validate_registration(data)

        if errors is not None:
            raise HTTPException(400, errors)

        hash_password = bcrypt.hashpw(bcrypt.hash(data.password1))
        register_data = {"email": data.email, "password": hash_password}
        user_id = await self.repo.create_user(register_data)
        return {"user_id": str(user_id)}

    async def login_user(self, data: LoginDTO):
        error_text = {"error": "username or password is wrong"}
        current_user = await self.repo.get_user_by_email(data.email)
        if current_user is None:
            return error_text
        verify = bcrypt.verify(data.password, current_user["password"])

        return "ok" if verify else "no"

    @classmethod
    def validate_registration(cls, data: dict) -> dict | None:
        error_pack = {}
        if data.password1 != data.password2:
            error_pack.update({"password": "password must be the same"})

        if error_pack:
            errors = {"code": status.HTTP_400_BAD_REQUEST, "messages": error_pack}
            return errors
        return None
