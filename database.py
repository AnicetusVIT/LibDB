# database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = None
db = None

def get_database():
    return db