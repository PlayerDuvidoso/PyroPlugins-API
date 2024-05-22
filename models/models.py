from pydantic import BaseModel, EmailStr
from typing import Optional

# --> Token Models <--
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str or None = None #type: ignore


# --> User Models <--
class User(BaseModel):
    username: str
    email: EmailStr or None = None #type: ignore
    disabled: Optional[bool] = False

class UserInDB(User):
    hashed_password: str

class UserInSignup(User):
    password: str

class UserAdmin(User):
    isAdmin: Optional[bool]=False