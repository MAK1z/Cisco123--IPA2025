import requests
import json
from dotenv import load_dotenv

load_dotenv()

requests.packages.urllib3.disable_warnings()


def configure_interface(
    router_ip, username, password, iface_name, iface_ip, iface_mask, is_enabled
):
    url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={iface_name}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
    }

    if "Loopback" in iface_name:
        iface_type = "iana-if-type:softwareLoopback"
    elif "Gigabit" in iface_name:
        iface_type = "iana-if-type:ethernetCsmacd"
    elif "Vlan" in iface_name:
        iface_type = "iana-if-type:l2vlan"
    else:
        iface_type = "iana-if-type:ethernetCsmacd"

    payload = {
        "ietf-interfaces:interface": {
            "name": iface_name,
            "type": iface_type,
            "enabled": is_enabled,
            "ietf-ip:ipv4": {"address": [{"ip": iface_ip, "netmask": iface_mask}]},
        }
    }

    try:
        if iface_ip == router_ip:  # git conflict here
            return True, "Configuration successful"
        elif iface_ip == "" and iface_mask == "":
            response = requests.delete(url, auth=(username, password), verify=False)
            response.raise_for_status()
        else:
            requests.delete(url, auth=(username, password), verify=False)
            response = requests.put(
                url,
                headers=headers,
                auth=(username, password),
                data=json.dumps(payload),
                verify=False,
            )
            response.raise_for_status()
        return True, "Configuration successful"

    except requests.exceptions.RequestException as e:
        error_message = f"Error configuring {iface_name} on {router_ip}: {e}"
        if e.response is not None:
            error_message += f" | Details: {e.response.text}"
        return False, error_message
