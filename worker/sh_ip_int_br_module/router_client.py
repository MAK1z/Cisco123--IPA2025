import requests
import json
import os
from dotenv import load_dotenv
from database import save_interface_status

load_dotenv()

requests.packages.urllib3.disable_warnings()

def get_interfaces(ip, username, password):

    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")

    if not mongo_uri or not db_name:
        print("Missing MONGO_URI or DB_NAME in .env")
        return

    url = f"https://{ip}/restconf/data/ietf-interfaces:interfaces"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    try:
        response = requests.get(url, headers=headers, auth=(username, password), verify=False)
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")
        return

    if response.status_code != 200:
        print(f"Failed to fetch interfaces from {ip}, status: {response.status_code}")
        print(response.text)
        return

    try:
        data = response.json()
    except json.JSONDecodeError:
        #print(f"[✗] Invalid JSON from {ip}")
        return

    if "ietf-interfaces:interfaces" not in data or "interface" not in data["ietf-interfaces:interfaces"]:
        #print(f"[✗] Unexpected RESTCONF data format from {ip}")
        print(json.dumps(data, indent=2))
        return

    interfaces = []
    for intf in data["ietf-interfaces:interfaces"]["interface"]:
        name = intf.get("name", "")
        enabled = intf.get("enabled", False)
        ipv4_list = intf.get("ietf-ip:ipv4", {}).get("address", [])
        ip_address = ipv4_list[0].get("ip", "") if ipv4_list else ""
        netmask = ipv4_list[0].get("netmask", "") if ipv4_list else ""

        interfaces.append({
            "interface": name,
            "ip_address": ip_address,
            "netmask": netmask,
            "status": "up" if enabled else "down",
            "proto": "up" if enabled else "down"
        })

    try:
        save_interface_status(ip, interfaces)
        print(f"Saved {len(interfaces)} interfaces from {ip} to MongoDB")
    except Exception as e:
        print(f"Failed to save data to MongoDB: {e}")

if __name__ == "__main__":
    get_interfaces()
