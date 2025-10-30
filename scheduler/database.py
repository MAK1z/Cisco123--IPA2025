import os

from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()

def get_router_info():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["routers"]
    router_data = routers.find()
    return router_data

def get_edit_interface():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")
    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["interface_config"]
    router_data = routers.find()
    return router_data

if __name__ == "__main__":
    get_router_info()
