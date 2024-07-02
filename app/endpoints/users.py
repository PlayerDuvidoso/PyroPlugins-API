from fastapi import APIRouter, Depends, HTTPException
from app.models.models import *
import app.models.pyrodb as pyrodb
from app.validation.auth import *

router = APIRouter()

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/users/{identifier}", response_model=UserProfile)
async def read_user(identifier: str):

    user = pyrodb.get_user_by_post(identifier)

    if not user:
        raise HTTPException(400, detail="Invalid Post!")

    return user
