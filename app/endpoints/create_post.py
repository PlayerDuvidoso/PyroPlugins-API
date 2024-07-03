from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.models import *
import app.models.pyrodb as pyrodb
from app.validation.auth import *
from app.validation.validator import Validate


router = APIRouter()
validate = Validate()


# --> Post Creation <--
@router.post("/create_post")
async def create_post(post_info: Post, user: User = Depends(get_current_active_user)) -> dict:

    user_email = user.model_dump()['email']

    if v := validate.post(post_info):
        raise HTTPException(400, detail=v)

    post_id = pyrodb.create_post(post_info, user_email)
    return {"status": 200, "detail": "Post created succesfully", "post_id": post_id}


@router.post("/create_post/{identifier}/upload")
async def upload_post_file(identifier: str, file: UploadFile = File(...), user: User = Depends(get_current_active_user)) -> dict:

    user_email = user.model_dump()['email']

    if v := validate.file(file):
        raise HTTPException(400, detail=v)
    
    pyrodb.create_post_plugin(identifier, user_email, file)
    return {"status": 200, "detail": "File added to the post succesfully"}