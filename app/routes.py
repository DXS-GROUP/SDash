import logging
import os
import platform
import subprocess
import time
from datetime import datetime
from logging.config import dictConfig

import psutil
import pynvml
from config import app, dictConfig
from flask import Flask, jsonify, redirect, render_template, request
from func import convert_seconds_to_hhmm
from get_info import (fetch_arch, fetch_cpu_info, get_ip_address,
                      get_open_ports_and_services, get_uptime, gpu_info,
                      model_info, os_name)

prev_net_io = psutil.net_io_counters()
prev_time = time.time()


@app.route("/api/ports")
def api_ports():
    ports_and_services = get_open_ports_and_services()
    return jsonify(ports_and_services)


@app.route("/api/server_clock", methods=["GET"])
def get_time():
    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%d %b %Y")

    return jsonify(current_time=current_time, current_date=current_date)


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
        cpu_arch=fetch_arch(),
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


@app.route("/api/gpu_temp")
def gpu_temp():
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count > 0:
            device = pynvml.nvmlDeviceGetHandleByIndex(0)
            return jsonify(
                gpu_temp=pynvml.nvmlDeviceGetTemperature(
                    device, pynvml.NVML_TEMPERATURE_GPU
                ),
                gpu_freq=pynvml.nvmlDeviceGetUtilizationRates(device).gpu,
            )
        return jsonify(gpu_temp="None", gpu_freq="None")
    except Exception as e:
        return jsonify(gpu_temp="None", gpu_freq="None", error=str(e))


@app.route("/api/disk_temperature", methods=["GET"])
def disk_temperature():
    disk_temp = get_disk_temperature()
    return jsonify(disk_temp) if disk_temp else jsonify(None)


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


@app.route("/get_os")
def get_os_color():
    os_name_str = os_name()
    return jsonify({"os_name": os_name_str})


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/actions/reboot", methods=["POST"])
def reboot_server():
    os.system("systemctl reboot")


@app.route("/api/actions/shutdown", methods=["POST"])
def shutdown_server():
    os.system("systemctl poweroff")


@app.route("/api/actions/sleep", methods=["POST"])
def sleep_server():
    os.system("systemctl suspend")


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404
