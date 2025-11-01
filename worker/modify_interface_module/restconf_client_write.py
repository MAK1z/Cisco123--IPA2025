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
        if iface_ip == router_ip:
            return True, "Configuration successful"
        elif (iface_ip == "" or iface_ip is None) and (iface_mask == "" or iface_mask is None):
            ipv4_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={iface_name}/ietf-ip:ipv4"
            get_resp = requests.get(ipv4_url, auth=(username, password), headers=headers, verify=False)
            if get_resp.status_code == 200:
                ipv4_data = get_resp.json()
                addresses = ipv4_data.get("ietf-ip:ipv4", {}).get("address", [])
                for addr in addresses:
                    ip = addr.get("ip")
                    if ip:
                        del_url = f"{ipv4_url}/address={ip}"
                        requests.delete(del_url, auth=(username, password), verify=False)
        else:
            ipv4_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces/interface={iface_name}/ietf-ip:ipv4"
            get_resp = requests.get(ipv4_url, auth=(username, password), headers=headers, verify=False)
            if get_resp.status_code == 200:
                ipv4_data = get_resp.json()
                addresses = ipv4_data.get("ietf-ip:ipv4", {}).get("address", [])
                for addr in addresses:
                    ip = addr.get("ip")
                    if ip:
                        del_url = f"{ipv4_url}/address={ip}"
                        requests.delete(del_url, auth=(username, password), verify=False)
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
        print(f"Error configuring")
        error_message = f"Error configuring {iface_name} on {router_ip}: {e}"
        if e.response is not None:
            error_message += f" | Details: {e.response.text}"
        return False, error_message
