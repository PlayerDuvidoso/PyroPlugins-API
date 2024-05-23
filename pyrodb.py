from decouple import config
from pymongo.mongo_client import MongoClient
from passlib.context import CryptContext
from models.models import *
from gridfs import GridFS
from os import remove, path, mkdir
import pendulum

# --> MongoDB Stuff <--
uri = config("URI_LINK")
db_con = MongoClient(uri)
db = db_con["PyroDB"]
fs = GridFS(db, "Files")
users = db["Users"]
files = db["Files.files"]


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
def get_user(email: str):
    user = users.find_one({'email': email})
    if user:
        return UserInDB(**user)

def add_user(username: str, email: str, password: str, disabled: bool = False, plugins: str = []):
    hashed_password = get_password_hash(password)
    user = UserInDB(username=username, email=email, hashed_password=hashed_password, disabled=disabled).model_dump()
    if users.find_one({"email": user['email']}):
        return False
    users.insert_one(user)
    return True

def append_plugin_to_owner(user_email: str, plugin_identifier: str):
    user = users.find_one({'email': user_email})
    if user:
        user_plugins: list = user['plugins']
        user_plugins.append(plugin_identifier)
        users.update_one({'email': user_email}, {'$set': {'plugins': user_plugins}})
    else:
        raise Exception("Couldn't append plugin to the user")


# --> File Upload Handle <--
def add_file(fileloc: str, filename: str, uuid: str, user_email: str):
    file = open(fileloc, 'rb+')
    fs.put(file, filename=filename, owner=user_email, identifier=uuid , total_downloads=0)
    file.close()
    append_plugin_to_owner(user_email, uuid)
    remove(fileloc)


# --> File Download Handle <--
def get_file(identifier: str):

    if not path.exists('CachedDownloads'):
        mkdir("CachedDownloads")


    data = files.find_one({"identifier": identifier})
    fs_id = data['_id']
    filename = data['filename']
    total_downloads = int(data['total_downloads']) + 1
    

    # --> Check if file is already in cache
    for i, file in enumerate(cache):

        if pendulum.now() >= file['expiry']:
            cache.pop(i)
            remove(file['path'])
            print(f'{file['filename']} was removed from cache!')

        if identifier == file['identifier'] and pendulum.now() < file['expiry']:
            
            print(f"{file['filename']} was found in cache!")
            
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
    print(f'{filename} was cached!')


    return DownloadInfo(path=output.name, name=filename).model_dump()