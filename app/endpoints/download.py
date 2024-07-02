from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.models import *
import app.models.pyrodb as pyrodb
from app.validation.auth import *


router = APIRouter()

# --> File Download Handle <--
@router.get("/download/{identifier}")
async def download(identifier: str) -> FileResponse:

    try:
        download = pyrodb.get_file(identifier)
        return(FileResponse(download['path'], filename=download['name'], media_type='application/java-archive'))
    except:
        raise HTTPException(400, detail="Couldn't download this file, check if the identifier is correct!")
