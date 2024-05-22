from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import *
import pyrodb
from auth.auth import *


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


# --> File Handling Routes <--
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    
    fileloc = "temp/" + file.filename.replace(" ", "_")
    #try:
    with open(fileloc, 'wb+') as f:
        while contents := file.file.read(2048 * 2048):
            f.write(contents)
        f.close()
    #except Exception as e:
    #    return {"error": e}
    #finally:
    file.file.close()
    print("File was cached!")
    pyrodb.add_file(file.filename.replace(" ", "_"))
    return {"message": f"Successfully uploaded {file.filename}"}