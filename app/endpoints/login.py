from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.models import *
import app.models.pyrodb as pyrodb
from app.validation.auth import *
from app.validation.validator import Validate

router = APIRouter()
validate = Validate()

# --> Authentication Routes <--
@router.post("/signup", tags=["authentication"])
def signup_for_account(form_data: UserInSignup):

    form_data = form_data.model_dump()

    if v:= validate.username(form_data["username"]):
        raise HTTPException(400, detail=v)

    if v := validate.email(form_data["email"]):
        raise HTTPException(400, detail=v)

    if v := validate.password(form_data['password']):
        raise HTTPException(400, detail=v)

    try:
        if code := pyrodb.add_user(**form_data):
            # emails.send_verification(form_data["email"], code)
            return {"status": 200, "detail": "Registered Succesfully!"}
        raise HTTPException(400, detail="Email in already in use!")
    except:
        raise HTTPException(400, detail="Please insert valid information!")

    
@router.post("/signin", response_model=Token, tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    email: str = form_data.username
    password: str = form_data.password

    if v := validate.email(email):
        raise HTTPException(400, detail=v)

    if v := validate.password(password):
        raise HTTPException(400, detail=v)


    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    try:
        access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    except:
        raise HTTPException(400, detail="Invalid email or password, make sure your credentials are correct")
    return {"access_token": access_token, "token_type": "bearer"}
