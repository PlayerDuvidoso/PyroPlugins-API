from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import *
import pyrodb
from auth.auth import *
import os
from uuid import uuid4


app = FastAPI()


# --> Authentication Routes <--
@app.post("/signin", response_model=Token, tags=["authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or passowrd", headers={"WWW-Authenticate": "Bearer"})
    
    access_token_expires = timedelta(minutes=ACESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup", tags=["authentication"])
def signup_for_account(form_data: UserInSignup):
    if pyrodb.add_user(**form_data.model_dump()):
        return {"status": "Registered Succesfully!"}
    return {"status": "Please insert valid information!"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# --> File Upload Handle <--
@app.post("/upload")
async def upload(file: UploadFile = File(...), user: User = Depends(get_current_active_user)):

    user_email = user.model_dump()['email']

    # --> Creating a Unique File
    file_uuid = str(uuid4())
    fileloc = "CachedUploads/" + file_uuid +".jar"

    if file.filename[-4::] != '.jar':
        raise HTTPException(400, detail="Content must be a java (.jar) file")

    if not os.path.exists("CachedUploads"):
        os.mkdir("CachedUploads")


    try:
        with open(fileloc, 'wb+') as f:
            while contents := file.file.read(2048 * 2048):
                f.write(contents)
            f.close()
    except Exception:
        return {"error": "Something went wrong while uploading file!"}
    finally:
        file.file.close()
        pyrodb.add_file(fileloc, file.filename, file_uuid, user_email)
    return {"message": f"Successfully uploaded {file.filename}"}


# --> File Download Handle <--
@app.get("/download")
async def download(identifier: str) -> FileResponse:


    try:
        download = pyrodb.get_file(identifier)
        return(FileResponse(download['download_path'], filename=download['download_name'], media_type='application/octet-stream'))
    except:
        raise HTTPException(400, detail="Couldn't download this file, check if the identifier is correct!")
