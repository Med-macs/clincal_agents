from app.models import User, UserType
from app.engine import SupabaseDep
from typing import Optional

class UserRepository:
    def __init__(self, session: SupabaseDep):
        self.session = session

    def get_by_email(self, email: str) -> Optional[User]:
        response = self.session.table("users").select("*").eq("email", email).execute()
        return User(**response.data[0]) if response.data else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        response = self.session.table("users").select("*").eq("id", user_id).execute()
        return User(**response.data[0]) if response.data else None

    def create(self, name: str, email: str, age: int, gender: str, user_type: UserType) -> User:
        user = User(
            name=name,
            email=email,
            age=age,
            gender=gender,
            user_type=user_type
        )
        response = self.session.table("users").insert(user.model_dump()).execute()
        return User(**response.data[0]) 