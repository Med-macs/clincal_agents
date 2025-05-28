from fastapi import APIRouter, HTTPException
from app.models import User, UserLogin, UserType
from app.engine import SupabaseDep
from app.repository.UserRepository import UserRepository

UserRouter = APIRouter(
    prefix="/users",
    tags=["users"],
    redirect_slashes=True
)

@UserRouter.post("/login", response_model=User)
def login_user(user_data: UserLogin, session: SupabaseDep):
    """Login or create a new user"""
    user_repository = UserRepository(session)
    
    # Check if user exists
    existing_user = user_repository.get_by_email(user_data.email)
    if existing_user:
        return existing_user
    
    # Create new user if doesn't exist
    return user_repository.create(
        name=user_data.name,
        email=user_data.email,
        age=user_data.age,
        gender=user_data.gender,
        user_type=user_data.user_type
    )

@UserRouter.get("/{user_id}", response_model=User)
def get_user(user_id: int, session: SupabaseDep):
    """Get user by ID"""
    user_repository = UserRepository(session)
    user = user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
