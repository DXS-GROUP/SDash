import logging
import os
import platform
import subprocess
import time
from logging.config import dictConfig

import psutil
import pynvml
from flask import Flask, jsonify, redirect, render_template

from get_info import (fetch_cpu_info, get_ip_address, get_uptime, gpu_info,
                      model_info, os_name)
from services import get_services

home_dir = os.path.expanduser("~")
log_file_path = os.path.join(home_dir, "/logs/ServerPanel.log")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
        },
    }
)

app = Flask(__name__)

prev_net_io = psutil.net_io_counters()
prev_time = time.time()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/usage")
def usage():
    global prev_net_io, prev_time

    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    net_io = psutil.net_io_counters()
    current_time = time.time()
    elapsed_time = current_time - prev_time

    bytes_recv = net_io.bytes_recv - prev_net_io.bytes_recv
    bytes_sent = net_io.bytes_sent - prev_net_io.bytes_sent

    prev_net_io = net_io
    prev_time = current_time

    speed_recv = bytes_recv / elapsed_time / 1024  # kB/s
    speed_sent = bytes_sent / elapsed_time / 1024  # kB/s

    return jsonify(
        cpu_usage=cpu_usage,
        ram_usage=ram_usage,
        ram_total=psutil.virtual_memory().total,
        ram_used=psutil.virtual_memory().used,
        disk_usage=disk_usage,
        disk_total=psutil.disk_usage("/").total,
        disk_used=psutil.disk_usage("/").used,
        net_recv=speed_recv,
        net_sent=speed_sent,
        cpu_freq=psutil.cpu_freq().current,
    )


@app.route("/system_info")
def get_info():
    device_ip = get_ip_address()

    device_uptime = get_uptime()

    device_info = os.uname()
    device_name = device_info.nodename

    return jsonify(
        device_uptime=device_uptime,
        device_ip=device_ip,
        sys_platform=os_name(),
        device_name=device_name,
        sys_model=model_info(),
        sys_cpu=fetch_cpu_info(),
        sys_gpu=gpu_info(),
    )


@app.route("/cpu_temp")
def cpu_temp():
    try:
        temperatures = psutil.sensors_temperatures().get("coretemp", [])

        if not temperatures:
            raise ValueError("No temperature data available for coretemp")

        core_temps = [temp.current for temp in temperatures]

        avg_temp = sum(core_temps) / len(core_temps)

        return jsonify(cpu_temp=avg_temp, cpu_freq=psutil.cpu_freq().current)
    except Exception as e:

        return jsonify(cpu_temp="N/A", error=str(e))


@app.route("/shutdown", methods=["POST"])
def shutdown():
    subprocess.call(["shutdown", "/s" if platform.system() == "Windows" else "now"])
    return redirect("/")


@app.route("/reboot", methods=["POST"])
def reboot():
    subprocess.call(["shutdown", "/r" if platform.system() == "Windows" else "reboot"])
    return redirect("/")


@app.route("/sleep", methods=["POST"])
def sleep():
    if platform.system() == "Windows":
        subprocess.call(["rundll32", "powrprof.dll,SetSuspendState", "0", "1", "0"])
    elif platform.system() == "Linux":
        subprocess.call(["systemctl", "suspend"])
    return redirect("/")


@app.route("/api/services", methods=["GET"])
def api_services():
    return jsonify(get_services())


@app.route("/api/service/<action>/<service_name>", methods=["POST"])
def manage_service(action, service_name):
    try:
        service = psutil.win_service_get(service_name)
        if action == "restart":
            service.restart()
        elif action == "stop":
            service.stop()
        elif action == "disable":
            service.stop()
            service.disable()
        return jsonify({"status": "success", "action": action, "service": service_name})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404


if __name__ == "__main__":
    app.run(debug=True, host=get_ip_address())
