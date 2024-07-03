import app.models.pyrodb as pyrodb
from app.models.models import * 
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

# --> Secrets <--
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")
ACESS_TOKEN_EXPIRE_MINUTES = int(config("ACESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")

def authenticate_user(email: EmailStr, password: str):
    user = pyrodb.get_user(email)
    if not user:
        return False
    try:
        if not pyrodb.verify_password(password, user.hashed_password):
            return False
    except:
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta or None = None): #type: ignore
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
        
        token_data = TokenData(email=email)
    
    except JWTError:
        raise credential_exception
    
    user = pyrodb.get_user(email=token_data.email)
    if user is None:
        raise credential_exception
    
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    return current_user