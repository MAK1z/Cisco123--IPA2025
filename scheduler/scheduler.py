import time

import os
from bson import json_util
from producer import produce
from database import get_router_info, get_edit_interface
from dotenv import load_dotenv

from producer_shrun import produce_config_job
from producer_modify_interface import produce_config_change_job

load_dotenv()


def scheduler():

    INTERVAL = 3
    next_run = time.monotonic()
    count = 0
    host = os.getenv("RABBITMQ_HOST")

    while True:
        now = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)
        now_str_with_ms = f"{now_str}.{ms:03d}"
        print(f"[{now_str_with_ms}] run #{count}")

        try:
            for data in get_router_info():
                body_bytes = json_util.dumps(data).encode("utf-8")
                produce(host, body_bytes)
                produce_config_job(host, body_bytes)
            edit_interfaces = list(get_edit_interface())
            routers = list(get_router_info())
            if edit_interfaces:
                for edit_data in edit_interfaces:
                    router_ip = edit_data.get("router_ip")
                    username = None
                    password = None
                    for router in routers:
                        if router["ip"] == router_ip:
                            username = router["username"]
                            password = router["password"]
                            break
                    job = {
                        "_id": edit_data.get("_id"),
                        "router_ip": router_ip,
                        "username": username,
                        "password": password,
                        "iface_name": edit_data.get("interface_name"),
                        "iface_ip": edit_data.get("ip_address"),
                        "iface_mask": edit_data.get("netmask"),
                        "is_enabled": edit_data.get("is_enabled", True),
                    }

                    body_bytes = json_util.dumps(job).encode("utf-8")
                    produce_config_change_job(host, body_bytes)
        except Exception as e:
            print(e)
            time.sleep(3)
        count += 1
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))


if __name__ == "__main__":
    scheduler()
