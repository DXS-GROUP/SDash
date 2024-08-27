import os
import time
import psutil
from flask import Flask, jsonify, render_template, request, send_file
from loguru import logger
from get_info import (fetch_cpu_info, get_ip_address, get_service_name,
                      get_uptime, gpu_info, model_info, os_name)

import platform, subprocess

home_dir = os.path.expanduser("~")
log_file = os.path.join(home_dir, "logs", "ServerPage.log")

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

    speed_recv = bytes_recv / elapsed_time / 1024  # kB/s
    speed_sent = bytes_sent / elapsed_time / 1024  # kB/s

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
            "cpu_freq": psutil.cpu_freq().current
        }
    )

@app.route("/system_info")
def get_info():
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
            "sys_platform": os_name(),
            "device_name": device_name,
            "sys_model": model_info(),
            "sys_cpu": fetch_cpu_info(),
            "sys_gpu": gpu_info(),
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
    log_directory = os.path.expanduser('~/logs/')
    files = os.listdir(log_directory) if os.path.exists(log_directory) else []
    return jsonify(files)

@app.route('/download', methods=['POST'])
def download():
    selected_file = request.form['file']
    file_path = os.path.join(os.path.expanduser('~/logs/'), selected_file)
    
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404

@app.route('/open_file', methods=['POST'])
def open_file():
    selected_file = request.json['file']
    file_path = os.path.join(os.path.expanduser('~/logs/'), selected_file)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return jsonify({'content': content})
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/shutdown', methods=['POST'])
def shutdown():
    if platform.system() == "Windows":
        subprocess.call(["shutdown", "/s", "/t", "1"])
    elif platform.system() == "Linux":
        subprocess.call(["shutdown", "now"])
    return redirect('/')

@app.route('/reboot', methods=['POST'])
def reboot():
    if platform.system() == "Windows":
        subprocess.call(["shutdown", "/r", "/t", "1"])
    elif platform.system() == "Linux":
        subprocess.call(["reboot"])
    return redirect('/')

@app.route('/sleep', methods=['POST'])
def sleep():
    if platform.system() == "Windows":
        subprocess.call(["rundll32", "powrprof.dll,SetSuspendState", "0", "1", "0"])
    elif platform.system() == "Linux":
        subprocess.call(["systemctl", "suspend"])
    return redirect('/')

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(debug=False, host=get_ip_address())
