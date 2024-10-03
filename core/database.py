import os
import pymongo
from dotenv import load_dotenv
load_dotenv()

client = pymongo.MongoClient(os.getenv(("DB_LOGIN")))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError as e:
    print(f"Configuration error: {e}")
except pymongo.errors.OperationFailure as e:
    print(f"Operation failure: {e}")
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"Server selection timeout error: {e}")
    exit(1)
database = client["cs3028_db"]
users_collection = database["users"]
students_collection = database["students"]
oppotunities_collection = database["opportunities"]