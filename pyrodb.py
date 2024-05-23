from decouple import config
from pymongo.mongo_client import MongoClient
from passlib.context import CryptContext
from models.models import *
from gridfs import GridFS
from os import remove, path, mkdir

# --> MongoDB Stuff <--
uri = config("URI_LINK")
db_con = MongoClient(uri)
db = db_con["PyroDB"]
fs = GridFS(db, "Files")
users = db["Users"]
files = db["Files.files"]


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
    #print(f"\n-=-=-=-\nPyroDB: File Upload requested!\nOwner: {user_email}\nIdentifier: {uuid}\nFilename: {filename}\n-=-=-=-\n")
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
    out_data = fs.get(fs_id).read()
    total_downloads = int(data['total_downloads']) + 1

    with open(f"CachedDownloads/{filename}", "wb+") as output:
        output.write(out_data)
        output.close()

    files.update_one({"identifier": identifier}, {"$set": {"total_downloads": total_downloads}})
    
    return DownloadInfo(download_path=output.name, download_name=filename).model_dump()