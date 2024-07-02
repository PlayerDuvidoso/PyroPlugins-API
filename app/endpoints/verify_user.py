from fastapi import APIRouter, HTTPException
from app.models.models import *
import app.models.pyrodb as pyrodb
from app.validation.auth import *

router = APIRouter()

@router.get("/verify_user/{code}", tags=["authentication"])
async def verify_user(code: str):

    codeData = jwt.decode(code, SECRET_KEY, ALGORITHM)
    key = codeData["key"]

    dbData = pyrodb.get_user(codeData["email"]).model_dump()
    user_key = dbData["key"]

    if dbData["isVerified"]:
        raise HTTPException(400, detail="User already verified!")
    
    if key == user_key:
        pyrodb.verify_user(key)
        return {"status": 200, "detail": "User verified successfully"}
    
    raise HTTPException(400, detail="Invalid key")