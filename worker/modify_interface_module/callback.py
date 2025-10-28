from bson import json_util
from .restconf_client_write import configure_interface

def callback(ch, method, props, body):
    job = json_util.loads(body.decode())
    print(f" [✓] Received config change job for {job['router_ip']}")
    try:
        configure_interface(
            router_ip=job["router_ip"],
            username=job["username"],
            password=job["password"],
            iface_name=job["interface_name"],
            iface_ip=job["ip_address"],
            iface_mask=job["netmask"],
            is_enabled=job["is_enabled"]
        )
    except Exception as e:
        print(f" [✗] Error processing job: {e}")