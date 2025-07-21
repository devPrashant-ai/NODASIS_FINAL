from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()


def get_mongo_client():
    """
    Connect to MongoDB using MONGO_URI from environment.
    Raises error if not found.
    """
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        raise ValueError("❌ Environment variable MONGO_URI not set. Please define it in your .env file or shell.")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")  # Test connection
        print("✅ MongoDB connection established.")
        return client
    except Exception as e:
        raise ConnectionError(f"❌ Failed to connect to MongoDB: {e}")