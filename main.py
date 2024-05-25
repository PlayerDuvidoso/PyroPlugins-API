from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import *
import pyrodb
from auth.auth import *
from validation.validator import Validate


app = FastAPI()
validate = Validate()


# --> Authentication Routes <--
@app.post("/signup", tags=["authentication"])
def signup_for_account(form_data: UserInSignup):

    form_data = form_data.model_dump()

    if v:= validate.username(form_data["username"]):
        raise HTTPException(400, detail=v)

    if v := validate.email(form_data["email"]):
        raise HTTPException(400, detail=v)

    if v := validate.password(form_data['password']):
        raise HTTPException(400, detail=v)

    try:
        if pyrodb.add_user(**form_data):
            return {"status": 200, "detail": "Registered Succesfully!"}
        raise HTTPException(400, detail="Email in already in use!")
    except:
        raise HTTPException(400, detail="Please insert valid information!")

    
@app.post("/signin", response_model=Token, tags=["authentication"])
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



@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# --> Post Creation <--
@app.post("/create_post")
async def create_post(post_info: Post, user: User = Depends(get_current_active_user)) -> dict:

    user_email = user.model_dump()['email']

    if v := validate.post(post_info):
        raise HTTPException(400, detail=v)

    post_id = pyrodb.create_post(post_info, user_email)
    return {"status": 200, "detail": "Post created succesfully", "post_id": post_id}


@app.post("/create_post/{identifier}/upload")
async def upload_post_file(identifier: str, file: UploadFile = File(...), user: User = Depends(get_current_active_user)) -> dict:

    user_email = user.model_dump()['email']

    if v := validate.file(file):
        raise HTTPException(400, detail=v)
    
    pyrodb.create_post_plugin(identifier, user_email, file)
    return {"status": 200, "detail": "File added to the post succesfully"}


# --> File Download Handle <--
@app.get("/download/{identifier}")
async def download(identifier: str) -> FileResponse:

    try:
        download = pyrodb.get_file(identifier)
        return(FileResponse(download['path'], filename=download['name'], media_type='application/java-archive'))
    except:
        raise HTTPException(400, detail="Couldn't download this file, check if the identifier is correct!")
