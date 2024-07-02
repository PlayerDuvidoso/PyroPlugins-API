from app.models.models import *
from fastapi import UploadFile


class Validate():
    
    def credential_lenght(self, credential: str, max_lenght: int = 100, min_lenght: int = 2) -> bool:
        
        if len(credential) > max_lenght:
            return False
        
        if len(credential) < min_lenght:
            return False
        
        return True
    
    def username(self, username: str):
        max_lenght = 25
        min_lenght = 3

        if not username.isalnum():
            print(username, username.isalnum())
            return "Username can only have Letters and Numbers"
        
        elif not self.credential_lenght(username, max_lenght, min_lenght):
            return "Username must have between 3 and 25 characters"
        
        return False

    def email(self, email: str):
        invalid_chars = r'\#!$%¨&*()-=+[{]}|'
        max_lenght = 50
        min_lenght = 5

        if not email.replace("@", "").replace(".", "").isalnum():
            return "Email contains illegal characters"
        
        elif any(c in invalid_chars for c in email):
            return "Email contains illegal characters"
        
        elif not self.credential_lenght(email, max_lenght, min_lenght):
            return "Email must have between 5 and 50 characters"
        
        return False
    

    def password(self, password: str):
        max_lenght = 32
        min_lenght = 8

        if not password.isascii():
            return "Password contains illegal characters"
        
        elif not self.credential_lenght(password, max_lenght, min_lenght):
            return "Password must have between 8 and 32 characters"
        
        return False
    
    def post(self, post: Post):

        post = post.model_dump()

        # --> Title
        post_title = post["title"]

        if not self.credential_lenght(post_title, 25):
            return "Post title must have between 2 and 25 characters"
        
        # --> About
        post_about = post["about"]

        if not self.credential_lenght(post_about, 50):
            return "Post about must have between 2 and 50 characters"
    
        # --> Description
        post_description = post["description"]

        if not self.credential_lenght(post_description, 1000):
            return "Post description must have between 2 and 1000 characters"
        
        return False
    
    def file(self, file: UploadFile):
        max_file_size = 50000000
        
        # --> Filename
        filename = file.filename

        if not self.credential_lenght(filename, 30, 6):
            return "Filename must have between 6 and 30 characters"
        
        # --> File Extension
        file_extension = filename[-4::]

        if file_extension != '.jar':
            return "File must be a jar"
        
        # --> File Size
        file_size = file.size

        if file_size > max_file_size:
            return "File size must be smaller than 50mb"

        return False

    