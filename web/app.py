import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from flask import Flask, request, render_template, redirect, url_for, flash
from pymongo import MongoClient
from dotenv import load_dotenv
import json
from bson import json_util

from scheduler.producer_modify_interface import produce_config_change_job


load_dotenv()
sample = Flask(__name__)

sample.secret_key = os.getenv("FLASK_SECRET_KEY", "a-very-secret-key-for-dev")

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("DB_NAME")
client = MongoClient(mongo_uri)
mydb = client[db_name]
mycol = mydb["routers"]
mycol2 = mydb["interface_status"]
mycol_config = mydb["running_config"]

@sample.route("/")
def main():
    data = mycol.find()
    return render_template("index.html", data=data)


@sample.route("/add", methods=["POST"])
def add_comment():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")
    if ip and username and password:
        info = {"ip": ip, "username": username, "password": password}
        mycol.insert_one(info)
        flash(f"Router {ip} added successfully!", "success")
    return redirect(url_for("main"))


@sample.route("/delete", methods=["POST"])
def delete_comment():
    data_list = list(mycol.find())
    try:
        idx = int(request.form.get("idx"))
        router_ip = data_list[idx]['ip']
        col = {"_id": data_list[idx]["_id"]}
        mycol.delete_one(col)
        flash(f"Router {router_ip} has been deleted.", "success")
    except Exception:
        flash("Error deleting router.", "error")
        pass
    return redirect(url_for("main"))


@sample.route("/router/<ip>")
def router_detail(ip):
    router = mycol.find_one({"ip": ip})
    status_list = list(mycol2.find({"router_ip": ip}).sort("timestamp", -1).limit(5))
    return render_template("router_detail.html", router=router, status_list=status_list)


@sample.route("/router/<ip>/config")
def running_config(ip):
    config_doc = mycol_config.find_one(
        {"router_ip": ip},
        sort=[("timestamp", -1)]
    )
    config_str = ""
    if config_doc and "running_config" in config_doc:
        config_str = json.dumps(
            config_doc["running_config"],
            indent=4,
            default=json_util.default
        )
    return render_template("running_config.html", ip=ip, config_data=config_str, timestamp=config_doc.get("timestamp"))

@sample.route("/router/<ip>/interfaces")
def interface_list(ip):
    router = mycol.find_one({"ip": ip})
    status_list = list(mycol2.find({"router_ip": ip}).sort("timestamp", -1).limit(1))
    return render_template("interface_list.html", router=router, status_list=status_list)

@sample.route("/router/<ip>/configure/<path:interface_name>")
def configure_interface_form(ip, interface_name):
    router = mycol.find_one({"ip": ip})
    current_ip = ""
    current_mask = ""
    is_enabled = True
    status_doc = mycol2.find_one(
        {"router_ip": ip},
        sort=[("timestamp", -1)]
    )
    
    if status_doc and "interfaces" in status_doc:
        for iface in status_doc["interfaces"]:
            if iface.get("interface") == interface_name:
                current_ip = iface.get("ip_address", "")
                current_mask = iface.get("netmask", "")
                is_enabled = iface.get("status", "down") == "up"
                break
    
    return render_template(
        "configure_interface.html",
        router=router,
        interface_name=interface_name,
        current_ip=current_ip,
        current_mask=current_mask,
        is_enabled=is_enabled
    )

@sample.route("/router/<ip>/configure/<path:interface_name>", methods=["POST"])
def submit_interface_config(ip, interface_name):
    router = mycol.find_one({"ip": ip})
    if not router:
        flash("Router not found!", "error")
        return redirect(url_for("main"))

    new_ip = request.form.get("ip_address")
    netmask = request.form.get("netmask")
    status = request.form.get("status")

    job_payload = {
        "router_ip": router["ip"],
        "username": router["username"],
        "password": router["password"],
        "interface_name": interface_name,
        "ip_address": new_ip,
        "netmask": netmask,
        "is_enabled": True if status == "enabled" else False
    }

    try:
        body_bytes = json.dumps(job_payload, default=json_util.default).encode("utf-8")
        produce_config_change_job(os.getenv("RABBITMQ_HOST"), body_bytes)
        flash(f"Configuration job for {interface_name} submitted successfully!", "success")
    except Exception as e:
        flash(f"Failed to submit job: {e}", "error")

    return redirect(url_for("router_detail", ip=ip))


if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=5050, debug=True)