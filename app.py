import os
import platform
import sys
import time
from logging import info
from os import environ
from os.path import exists, isfile
from subprocess import DEVNULL, PIPE, Popen

import psutil
from flask import Flask, jsonify, render_template

from get_info import fetch_cpu_info, gpu_info, model_info, os_name

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

    device_info = os.uname()
    device_name = device_info.nodename

    return jsonify(
        {
            "sys_platform": sys_platform,
            "device_name": device_name,
            "sys_model": sys_model,
            "sys_cpu": sys_cpu,
            "sys_gpu": sys_gpu,
        }
    )


if __name__ == "__main__":
    app.run(debug=False, port="3098")
