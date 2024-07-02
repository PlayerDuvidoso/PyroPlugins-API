from fastapi import FastAPI
from app.endpoints import login, users, download, create_post, verify_user

app = FastAPI()

app.include_router(login.router)
app.include_router(users.router)
app.include_router(download.router)
app.include_router(verify_user.router)
app.include_router(create_post.router)