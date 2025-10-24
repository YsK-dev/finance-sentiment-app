from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Optional

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

mongodb = MongoDB()

async def connect_db():
    """Connect to MongoDB"""
    try:
        mongodb.client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        mongodb.database = mongodb.client[os.getenv("DB_NAME", "finance_sentiment")]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise

async def close_db():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return mongodb.database
