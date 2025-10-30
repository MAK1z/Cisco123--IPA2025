from pymongo import MongoClient
from datetime import datetime, UTC
import os
from bson import ObjectId
from dotenv import load_dotenv
load_dotenv()
def get_db_collection(collection_name):
    """คืนค่า collection และ client object"""
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME")
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[collection_name], client


def save_interface_status(router_ip, interfaces):
    collection, client = get_db_collection("interface_status")
    data = {
        "router_ip": router_ip,
        "timestamp": datetime.now(UTC),
        "interfaces": interfaces,
    }
    limit_collection_size(collection, router_ip, 3)
    collection.insert_one(data)
    client.close()


def save_running_config(router_ip, running_config):
    collection, client = get_db_collection("running_config")
    data = {
        "router_ip": router_ip,
        "timestamp": datetime.now(UTC),
        "running_config": running_config,
    }
    limit_collection_size(collection, router_ip, 3)
    collection.insert_one(data)
    client.close()


def limit_collection_size(collection, router_ip, max_docs):
    count = collection.count_documents({"router_ip": router_ip})
    if count >= max_docs:
        oldest = collection.find_one({"router_ip": router_ip}, sort=[("timestamp", 1)])
        if oldest:
            collection.delete_one({"_id": oldest["_id"]})


def delete_interface_config(doc_id):
    collection, client = get_db_collection("interface_config")
    if not isinstance(doc_id, ObjectId):
        doc_id = ObjectId(doc_id)

    result = collection.delete_one({"_id": doc_id})
    client.close()
