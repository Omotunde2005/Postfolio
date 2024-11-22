import os
from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
from dotenv import load_dotenv


load_dotenv()
MONGODB_URL = os.environ.get("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.users
users_collection = db.get_collection("users")
boards_collection = db.get_collection("boards")