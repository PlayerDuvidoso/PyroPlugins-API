from decouple import config
from fastapi import HTTPException, UploadFile
from pymongo.mongo_client import MongoClient
from passlib.context import CryptContext
from models.models import *
from gridfs import GridFS
from os import remove, mkdir, scandir, path
from shutil import rmtree
import pendulum
from uuid import uuid4

# --> MongoDB Stuff <--
uri = config("URI_LINK")
db_con = MongoClient(uri)
db = db_con["PyroDB"]
fs = GridFS(db, "Files")
users = db["Users"]
files = db["Files.files"]
posts = db["Posts"]


# --> Cache <--
cache_duration = float(config("CACHE_EXPIRE_MINUTES"))
cache = []


# --> Encryption <--
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


# --> User Handling <--
def get_user(email: str) -> UserInDB:
    user = users.find_one({'email': email})
    if user:
        return UserInDB(**user)

def add_user(username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    key = str(uuid4())
    user = UserInDB(username=username, email=email, key=key, hashed_password=hashed_password).model_dump()
    if users.find_one({"email": user['email']}):
        return False
    users.insert_one(user)
    return True

def append_post_to_owner(user_email: str, post_identifier: str):
    user = users.find_one({'email': user_email})
    if user:
        user_posts: list = user['posts']
        user_posts.append(post_identifier)
        users.update_one({'email': user_email}, {'$set': {'posts': user_posts}})
    else:
        raise HTTPException(400, "Couldn't append post to the user")
    
def verify_user(key) -> None:
    users.update_one({"key": key}, {"$set": {'isVerified': True}})



# --> Post Handling <--
def create_post(post: Post, user_email: str) -> str:
    identifier = str(uuid4())
    post_to_create = PostInDB(identifier=identifier, owner=user_email, **post.model_dump()).model_dump()
    
    posts.insert_one(post_to_create)
    append_post_to_owner(user_email, identifier)

    return identifier


def create_post_plugin(identifier: str, user_email: str, file: UploadFile):
    if not path.exists("CachedUploads"):
        mkdir("CachedUploads")
    
    fileloc = "CachedUploads/"+identifier+".jar"

    plugin = PluginInDB(filename=file.filename, owner=user_email, identifier=identifier, total_downloads=0).model_dump()
    
    try:
        with open(fileloc, 'wb+') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)                
            f.close()
        file.file.close()
        fs.put(open(fileloc, 'rb+'), **plugin)
        remove(fileloc)

    except:
        raise HTTPException(400, detail="Something went wrong while uploading file!")



# --> File Download Handle <--
def get_file(identifier: str):

    # --> Check if there is leftover cache if server was restarted/crashed
    if len(cache) == 0:
        try:
            with scandir('CachedDownloads') as it:
                if any(it):
                    rmtree("CachedDownloads")     
                    mkdir("CachedDownloads")  
        except:
            mkdir("CachedDownloads")


    # --> Getting File Info
    data = files.find_one({"identifier": identifier})
    fs_id = data['_id']
    filename = data['filename']
    total_downloads = int(data['total_downloads']) + 1
    

    # --> Check if file is already in cache
    for i, file in enumerate(cache):

        if pendulum.now() >= file['expiry']: # Clears Expired cache
            cache.pop(i)
            remove(file['path'])

        if identifier == file['identifier'] and pendulum.now() < file['expiry']: # If file isn't expired and cached returns it to server       
            files.update_one({"identifier": identifier}, {"$set": {"total_downloads": total_downloads}})
            return DownloadInfo(path=file['path'], name=file['filename']).model_dump()

    
    # --> If file isn't cached, get from DB and cache it
    out_data = fs.get(fs_id).read()
    with open(f"CachedDownloads/{identifier}.jar", "wb+") as output:
        output.write(out_data)
        output.close()

    files.update_one({"identifier": identifier}, {"$set": {"total_downloads": total_downloads}})
    
    to_cache = DownloadCache(identifier=identifier, filename=filename, path=output.name, expiry=(pendulum.now() + pendulum.duration(minutes=cache_duration))).model_dump()
    cache.append(to_cache)

    return DownloadInfo(path=output.name, name=filename).model_dump()