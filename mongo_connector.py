# mongo_connector.py

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

def get_mongo_connection(db_name="admin"):
    """
    Returns a handle to the specified MongoDB database.
    URI is loaded from .env as MONGODB_URI.
    """
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    return db
