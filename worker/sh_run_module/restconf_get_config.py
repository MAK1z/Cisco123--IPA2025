import requests
import json
import os
from dotenv import load_dotenv
from database import save_running_config

load_dotenv()

requests.packages.urllib3.disable_warnings()

def get_running_config(ip, username, password):
    url = f"https://{ip}/restconf/data/Cisco-IOS-XE-native:native"
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    try:
        response = requests.get(url, headers=headers, auth=(username, password), verify=False)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {ip}: {e}")
        return

    try:
        data = response.json()
        config_data = data.get("Cisco-IOS-XE-native:native", {})
        
        if not config_data:
            print(f"Could not find 'Cisco-IOS-XE-native:native' key in response from {ip}")
            return

        save_running_config(ip, config_data)
        print(f"Successfully saved running-config for {ip} to MongoDB.")

    except json.JSONDecodeError:
        print(f"Invalid JSON received from {ip}")
    except Exception as e:
        print(f"An error occurred while saving to MongoDB: {e}")