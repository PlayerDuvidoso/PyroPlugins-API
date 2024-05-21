from decouple import config
from pymongo.mongo_client import MongoClient
from passlib.context import CryptContext
from models.models import UserInDB
from fastapi.security import OAuth2PasswordBearer

# --> MongoDB Stuff <--
uri = config("URI_LINK")
db_con = MongoClient(uri)
db = db_con["PyroDB"]
users = db["Users"]


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)