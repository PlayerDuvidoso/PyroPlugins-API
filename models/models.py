from pydantic import BaseModel

# --> Authentication Models <--
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None #type: ignore

class User(BaseModel):
    username: str
    email: str or None = None #type: ignore
    full_name: str or None = None #type: ignore
    disabled: bool or None = None #type: ignore

class UserInDB(User):
    hashed_password: str