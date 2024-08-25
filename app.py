import os
import platform
import socket
import subprocess
import sys
import time
from logging import info
from os import environ
from os.path import exists, isfile
from subprocess import DEVNULL, PIPE, Popen

import psutil
from flask import Flask, jsonify, render_template

from get_info import (fetch_cpu_info, get_ip_address, get_uptime, gpu_info,
                      model_info, os_name)

app = Flask(__name__)

prev_bytes_recv = psutil.net_io_counters().bytes_recv
prev_bytes_sent = psutil.net_io_counters().bytes_sent
prev_time = time.time()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/usage")
def usage():
    global prev_bytes_recv, prev_bytes_sent, prev_time

    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    net_io = psutil.net_io_counters()
    current_time = time.time()
    elapsed_time = current_time - prev_time

    bytes_recv = net_io.bytes_recv - prev_bytes_recv
    bytes_sent = net_io.bytes_sent - prev_bytes_sent

    prev_bytes_recv = net_io.bytes_recv
    prev_bytes_sent = net_io.bytes_sent

    prev_time = current_time

    speed_recv = bytes_recv / elapsed_time / 1024
    speed_sent = bytes_sent / elapsed_time / 1024

    # speed_recv = speed_recv / 1024
    # speed_sent = speed_sent / 1024

    return jsonify(
        {
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "disk_usage": disk_usage,
            "net_recv": speed_recv,
            "net_sent": speed_sent,
        }
    )


@app.route("/system_info")
def get_info():
    sys_platform = os_name()
    sys_model = model_info()
    sys_cpu = fetch_cpu_info()
    sys_gpu = gpu_info()

    device_ip = get_ip_address()

    device_uptime = get_uptime()

    device_info = os.uname()
    device_name = device_info.nodename

    return jsonify(
        {
            "device_uptime": device_uptime,
            "device_ip": device_ip,
            "sys_platform": sys_platform,
            "device_name": device_name,
            "sys_model": sys_model,
            "sys_cpu": sys_cpu,
            "sys_gpu": sys_gpu,
        }
    )


@app.route("/cpu_temp")
def cpu_temp():
    try:
        cpu_temp = psutil.sensors_temperatures()["coretemp"][0].current
        return jsonify({"cpu_temp": cpu_temp})
    except Exception as e:
        return jsonify({"cpu_temp": "N/A", "error": str(e)})


@app.route('/services', methods=['GET'])
def list_services():
    try:
        output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--state=active,inactive,failed'], universal_newlines=True)
        services = []
        for line in output.strip().split('\n')[1:]:
            if line.strip():  # Check if the line is not empty
                service_name = line.split()[0]
                services.append(service_name)
        return jsonify(services)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500


@app.route("/services/<service_name>/start", methods=["POST"])
def start_service(service_name):
    try:
        subprocess.check_call(["systemctl", "start", service_name])
        return (
            jsonify({"message": f"Service {service_name} started successfully."}),
            200,
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/services/<service_name>/stop", methods=["POST"])
def stop_service(service_name):
    try:
        subprocess.check_call(["systemctl", "stop", service_name])
        return (
            jsonify({"message": f"Service {service_name} stopped successfully."}),
            200,
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/services/<service_name>/restart", methods=["POST"])
def restart_service(service_name):
    try:
        subprocess.check_call(["systemctl", "restart", service_name])
        return (
            jsonify({"message": f"Service {service_name} restarted successfully."}),
            200,
        )
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, port="3098", host=get_ip_address())
