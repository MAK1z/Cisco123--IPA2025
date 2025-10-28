import requests
import json
from dotenv import load_dotenv

load_dotenv()

requests.packages.urllib3.disable_warnings()

def configure_interface(router_ip, username, password, iface_name, iface_ip, iface_mask, is_enabled):
    url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={iface_name}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
    }

    payload = {
        "ietf-interfaces:interface": {
            "name": iface_name,
            "enabled": is_enabled,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": iface_ip,
                        "netmask": iface_mask
                    }
                ]
            }
        }
    }

    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=(username, password),
            data=json.dumps(payload),
            verify=False
        )
        response.raise_for_status()
        #print(f"[✓] Successfully configured interface {iface_name} on {router_ip}")
        return True, "Configuration successful"

    except requests.exceptions.RequestException as e:
        error_message = f"Error configuring {iface_name} on {router_ip}: {e}"
        if e.response is not None:
            error_message += f" | Details: {e.response.text}"
        #print(f"[✗] {error_message}")
        return False, error_message