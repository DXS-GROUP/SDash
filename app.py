import os
import platform
import socket
import sys
import time
from os import environ
from os.path import exists, isfile
from subprocess import DEVNULL, PIPE, Popen

import psutil
from flask import Flask, jsonify, render_template, request, send_file
from loguru import logger

from get_info import (fetch_cpu_info, get_ip_address, get_service_name,
                      get_uptime, gpu_info, model_info, os_name)

home_dir = os.environ["HOME"]
log_file = home_dir + "/logs/ServerPage.log"

logger.add(
    log_file,
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100 MB",
    compression="zip",
)

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

    logger.debug(f"CPU Usage: {cpu_usage}%")
    logger.debug(f"RAM Usage: {ram_usage}%")
    logger.debug(f"Disk Usage: {disk_usage}%")
    logger.debug(f"Download Speed: {speed_recv:.2f} kB/s")
    logger.debug(f"Upload Speed: {speed_sent:.2f} kB/s")

    return jsonify(
        {
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "ram_total": psutil.virtual_memory().total,
            "ram_used": psutil.virtual_memory().used,
            "disk_usage": disk_usage,
            "disk_total": psutil.disk_usage("/").total,
            "disk_used": psutil.disk_usage("/").used,
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
    logger.info(f"Device IP: {device_ip}")

    device_uptime = get_uptime()
    logger.info(f"Device Uptime: {device_uptime}")

    device_info = os.uname()
    device_name = device_info.nodename
    logger.info(f"Device Name: {device_name}")

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
        logger.debug(f"CPU Temperature: {cpu_temp:.2f}°C")
        return jsonify({"cpu_temp": cpu_temp})
    except Exception as e:
        logger.error(f"Error getting CPU temperature: {e}")
        return jsonify({"cpu_temp": "N/A", "error": str(e)})


@app.route('/files')
def files():
    # Получаем список файлов из папки ~/logs/
    log_directory = os.path.expanduser('~/logs/')
    if os.path.exists(log_directory):
        files = os.listdir(log_directory)
    else:
        files = []
    return jsonify(files)

@app.route('/download', methods=['POST'])
def download():
    selected_file = request.form['file']  # Получаем имя файла из формы
    file_path = os.path.join(os.path.expanduser('~/logs/'), selected_file)
    
    # Проверяем, существует ли файл перед отправкой
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/open_file', methods=['POST'])
def open_file():
    selected_file = request.json['file']  # Используем request.json для получения JSON-данных
    file_path = os.path.join(os.path.expanduser('~/logs/'), selected_file)

    # Читаем содержимое файла
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(debug=False, port="3098", host=get_ip_address())
