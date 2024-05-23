from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

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
    
class UserPlugins(User):
    plugins: Optional[list] = []

class UserInDB(UserPlugins):
    hashed_password: str

class UserInSignup(User):
    password: str

class UserAdmin(User):
    isAdmin: Optional[bool]=False


# --> Plugin Management Models <--
class DownloadInfo(BaseModel):
    path: str
    name: str

class DownloadCache(BaseModel):
    identifier: str
    filename: str
    path: str
    expiry: datetime