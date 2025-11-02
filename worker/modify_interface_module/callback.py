from bson import json_util, ObjectId
from .restconf_client_write import configure_interface
from database import delete_interface_config, get_db_collection


def callback(ch, method, props, body):
    job = json_util.loads(body.decode())
    mycol_interface_status, client = get_db_collection("interface_status")
    router_ip = job.get("router_ip")
    try:
        configure_interface(
            router_ip=router_ip,
            username=job.get("username"),
            password=job.get("password"),
            iface_name=job.get("iface_name"),
            iface_ip=job.get("iface_ip"),
            iface_mask=job.get("iface_mask"),
            is_enabled=job.get("is_enabled"),
            last_config=list(
                mycol_interface_status.find({"router_ip": router_ip})
                .sort("timestamp", -1)
                .limit(1)
            ),
        )

        doc_id = job.get("_id")
        if isinstance(doc_id, dict) and "$oid" in doc_id:
            doc_id = ObjectId(doc_id["$oid"])
        elif isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        elif not isinstance(doc_id, ObjectId):
            raise ValueError("Invalid _id format")
        delete_interface_config(doc_id)
    except Exception:
        print("Error")
