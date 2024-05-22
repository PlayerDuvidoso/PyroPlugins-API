from decouple import config
from pymongo.mongo_client import MongoClient
from passlib.context import CryptContext
from models.models import *
from gridfs import GridFS
from os import remove

# --> MongoDB Stuff <--
uri = config("URI_LINK")
db_con = MongoClient(uri)
db = db_con["PyroDB"]
fs = GridFS(db, "Files")
users = db["Users"]


# --> Encryption <--
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


# --> User Handling <--
def get_user(email: str):
    user = users.find_one({'email': email})
    if user:
        return UserInDB(**user)

def add_user(username: str, email: str, password: str, disabled: bool = False):
    hashed_password = get_password_hash(password)
    user = UserInDB(username=username, email=email, hashed_password=hashed_password, disabled=disabled).model_dump()
    if users.find_one({"email": user['email']}):
        return False
    users.insert_one(user)
    return True

# --> File Handling <--
def add_file(filename):
    temp = f'temp/{filename}'
    file = open(temp, 'rb+')
    fs.put(file, filename=filename)
    file.close()
    remove(temp)
    print("File was Uploaded Successfully!")