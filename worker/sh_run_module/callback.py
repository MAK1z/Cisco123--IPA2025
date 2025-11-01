from bson import json_util
from .restconf_get_config import get_running_config

def callback(ch, method, props, body):
    job = json_util.loads(body.decode())
    router_ip = job["ip"]
    router_username = job["username"]
    router_password = job["password"]
    print(f"Received config job for router {router_ip}")
    try:
        get_running_config(router_ip, router_username, router_password)
    except Exception as e:
        print(f"Error: {e}")