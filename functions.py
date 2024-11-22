import urllib
import secrets
import string
import requests
import settings
import jwt
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from schema import UserRegistrationSchema
from models import User

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


    # @classmethod
    # def generate_session_id():
    #     return str(uuid.uuid4())


class Token:

    @classmethod
    def generate_random_token(cls):
        characters = string.ascii_letters
        return ''.join(secrets.choice(characters) for _ in range(20))
    
    @classmethod
    def generate_access_token(cls, data_to_encode: dict, expires_in: timedelta):
        data_to_encode = data_to_encode.copy()
        expiry = datetime.now(timezone.utc) + expires_in
        data_to_encode.update({"exp": expiry})
        encoded_jwt = jwt.encode(data_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt 



class UserAuth:

    @classmethod
    def get_hashed_password(cls, password):
        return PWD_CONTEXT.hash(password)
    
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return PWD_CONTEXT.verify(plain_password, hashed_password)

    @classmethod
    def get_user(cls, db, username):
        user = db.get(username, None)
        if user:
            user = UserRegistrationSchema(**user)
            return user

    @classmethod
    async def authenticate_user(cls, db, email: str, password: str):
        user = await db.find_one({"email": email})
        if not user:
            return False
        
        if not cls.verify_password(password, user["password"]):
            return False
        
        return User(**user)


class SocialMedia:
    twitter_embed = """
    <blockquote class="twitter-tweet"><p lang="en" dir="ltr">✅ I like to be convinced whenever I&#39;m reading an article or how to guide that solves a problem.<br><br>✅ I need to know why you added a new variable to the settings file. <br><br>✅ And real life examples? I love them so much.<br><br>This is the same energy I put into my writing.</p>&mdash; Emiloju. py (@emiloju_py) <a href="https://twitter.com/emiloju_py/status/1739548333981548870?ref_src=twsrc%5Etfw">December 26, 2023</a></blockquote>
    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
    """

    linkedin_embed = """ """

    @classmethod
    async def generate_tweet_embed(cls, tweet_url):
        encoded_url = urllib.parse.quote(tweet_url)
        url = f"https://publish.twitter.com/oembed?url={encoded_url}&max-width=500"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["html"]
            

    @classmethod
    async def is_valid_linkedin_embed(cls, embed_code):
        soup = BeautifulSoup(embed_code, "html.parser")

        iframe = soup.find("iframe")

        if iframe:
            return True
        return False


    @classmethod
    def modify_linkedin_embed(cls, embed_code: str, max_width="500px", max_height="500px"):
        soup = BeautifulSoup(embed_code, "html.parser")


        for iframe in soup.find_all("iframe"):
            del iframe["height"]
            iframe["style"] = f"max-width: {max_width}; max-height: {max_height};"

        return soup
    
    @classmethod
    def modify_x_embed(cls, embed_code: str, max_width="500px", max_height="500px"):
        soup = BeautifulSoup(embed_code, "html.parser")

        for blockquote in soup.find_all("blockquote"):
            if blockquote:
                blockquote["style"] = f"max-width: {max_width}; max-height: {max_height};"

        return soup

    @classmethod
    def edit_post(cls, post_dict: dict, new_post: str):
        post_dict["post"] = new_post
        return post_dict