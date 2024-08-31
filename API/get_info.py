import platform
import socket
import sys
import time
from os import environ, path
from subprocess import DEVNULL, PIPE, Popen

import psutil
from API.func import convert_seconds_to_hhmm, truncate_string, run_command

def get_uptime():
    if platform.system() != "Linux":
        return "Error."

    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])

    return f"{round(uptime_seconds // 86400)}d {round(uptime_seconds % 86400 // 3600)}h {round(uptime_seconds % 3600 // 60)}m {uptime_seconds % 60:.0f}s"

def get_ip_address():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

def os_name():
    os_file = "/etc/os-release" if path.isfile("/etc/os-release") else "/bedrock/etc/os-release"
    return run_command(f"grep 'PRETTY_NAME' {os_file}").replace('PRETTY_NAME=', '').replace('"', '')

def model_info():
    product_info = run_command("cat /sys/devices/virtual/dmi/id/product_name").strip()
    version_info = run_command("cat /sys/devices/virtual/dmi/id/product_version").strip()
    return f"{product_info} {version_info}" if version_info else product_info

def fetch_cpu_info():
    cpu_count = len(run_command("ls /sys/class/cpuid/ | sort").splitlines())
    cpu_info = run_command("grep 'model name' /proc/cpuinfo").split(":")[1].strip()
    cpu_max_freq = int(run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")) / 1000
    cpu_freq_info = f"{cpu_max_freq:.3f}MHz" if cpu_max_freq < 1000 else f"{cpu_max_freq / 1000:.3f}GHz"
    return f"{cpu_info} ({cpu_count}) @ {cpu_freq_info}"

def gpu_info():
    if sys.platform == "darwin":
        return run_command("system_profiler SPDisplaysDataType | awk '/Chipset Model:/ {print $3, $4, $5, $6, $7}'").strip()

    if path.exists("/sys/class/dmi/id/product_name"):
        return truncate_string(run_command("lspci | grep -i vga").split(":")[2].split("(")[0].strip(), 50)

    return ""
