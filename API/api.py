import logging
import os
import platform
import subprocess
import time
from logging.config import dictConfig

import psutil
from flask import Flask, jsonify, redirect, render_template, request

from API.func import convert_seconds_to_hhmm
from API.get_info import (fetch_cpu_info, get_ip_address, get_uptime, gpu_info,
                          model_info, os_name)
from config import app, dictConfig

prev_net_io = psutil.net_io_counters()
prev_time = time.time()


@app.route("/api/usage")
def usage():
    global prev_net_io, prev_time

    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    net_io = psutil.net_io_counters()
    current_time = time.time()
    elapsed_time = current_time - prev_time

    bytes_recv = net_io.bytes_recv - prev_net_io.bytes_recv
    bytes_sent = net_io.bytes_sent - prev_net_io.bytes_sent

    prev_net_io, prev_time = net_io, current_time

    speed_recv = bytes_recv / elapsed_time / 1024  # kB/s
    speed_sent = bytes_sent / elapsed_time / 1024  # kB/s

    return jsonify(
        cpu_usage=cpu_usage,
        ram_usage=ram.percent,
        ram_total=ram.total,
        ram_used=ram.used,
        disk_usage=disk.percent,
        disk_total=disk.total,
        disk_used=disk.used,
        net_recv=speed_recv,
        net_sent=speed_sent,
        cpu_freq=psutil.cpu_freq().current,
    )


@app.route("/api/system_info")
def get_info():
    return jsonify(
        device_uptime=get_uptime(),
        device_ip=get_ip_address(),
        sys_platform=os_name(),
        device_name=os.uname().nodename,
        sys_model=model_info(),
        sys_cpu=fetch_cpu_info(),
        sys_gpu=gpu_info(),
    )


@app.route("/api/cpu_temp")
def cpu_temp():
    try:
        temperatures = psutil.sensors_temperatures().get("coretemp", [])
        if not temperatures:
            raise ValueError("No temperature data available for coretemp")

        avg_temp = sum(temp.current for temp in temperatures) / len(temperatures)
        return jsonify(cpu_temp=avg_temp, cpu_freq=psutil.cpu_freq().current)
    except Exception as e:
        return jsonify(cpu_temp="N/A", error=str(e))


@app.route("/api/actions/<action>", methods=["POST"])
def perform_action(action):
    actions = {
        "shutdown": ["shutdown", "/s" if platform.system() == "Windows" else "now"],
        "reboot": ["shutdown", "/r" if platform.system() == "Windows" else "reboot"],
        "sleep": (
            ["rundll32", "powrprof.dll,SetSuspendState", "0", "1", "0"]
            if platform.system() == "Windows"
            else ["systemctl", "suspend"]
        ),
    }

    if action in actions:
        subprocess.call(actions[action])
        return redirect("/")
    return jsonify({"error": "Invalid action"}), 400


@app.route("/api/battery", methods=["GET"])
def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        charge = battery.percent
        plugged = battery.power_plugged
        time_to_full = (
            convert_seconds_to_hhmm(battery.secsleft)
            if plugged and battery.secsleft != psutil.POWER_TIME_UNKNOWN
            else None
        )
        time_to_empty = (
            convert_seconds_to_hhmm(battery.secsleft)
            if not plugged and battery.secsleft != psutil.POWER_TIME_UNKNOWN
            else None
        )

        return jsonify(
            charge=charge,
            plugged=plugged,
            time_to_full=time_to_full,
            time_to_empty=time_to_empty,
        )
    return jsonify(charge=None, plugged=None, time_to_full=None, time_to_empty=None)


@app.route("/api/user_ip")
def get_user_ip():
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    return jsonify({"ip": ip_address})


@app.route("/navigate", methods=["POST"])
def navigate():
    page = request.form["page"]
    return f"Navigating to {page} page"

@app.route('/get_os')
def get_os_color():
    os_name_str = os_name()
    return jsonify({'os_name': os_name_str})
