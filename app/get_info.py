import platform
import socket
import sys
import time
from os import environ, path
from subprocess import DEVNULL, PIPE, Popen

import psutil
from func import truncate_string


def run_command(command):
    """Run a shell command and return the output."""
    with Popen(command, shell=True, stdout=PIPE, stderr=DEVNULL) as proc:
        output, _ = proc.communicate()
    return output.decode().strip()


def get_open_ports_and_services():
    connections = psutil.net_connections(kind="inet")
    open_ports = {}

    for conn in connections:
        localAddress, localPort = conn.laddr
        pid = conn.pid

        if pid is not None:
            try:
                process = psutil.Process(pid)
                service_name = process.name()
                username = process.username()
                status = "Running"  # Default status if no exceptions occur
                open_ports[localPort] = {
                    "service": service_name,
                    "user": username,
                    "status": status,
                }
            except psutil.NoSuchProcess:
                open_ports[localPort] = {
                    "service": "Unknown service",
                    "user": "Unknown user",
                    "status": "No such process",
                }
            except psutil.AccessDenied:
                open_ports[localPort] = {
                    "service": "Access denied",
                    "user": "Access denied",
                    "status": "Access denied",
                }
            except Exception as e:
                open_ports[localPort] = {
                    "service": "Error retrieving service",
                    "user": "Unknown user",
                    "status": f"Error: {str(e)}",
                }

    return open_ports


def get_uptime():
    """Get system uptime."""
    if platform.system() == "Linux":
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
        return f"{round(uptime_seconds // 86400)} days {round(uptime_seconds % 86400 // 3600)} hours {round(uptime_seconds % 3600 // 60)} minutes"
    elif platform.system() == "Windows":
        return run_command(
            "net stats workstation | findstr /C:'Statistics since'"
        )  # Windows uptime command
    elif platform.system() == "Darwin":  # macOS
        return run_command("uptime")  # macOS uptime command
    else:
        return "Unsupported OS for uptime retrieval."


def get_ip_address():
    """Get the local IP address."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def os_name():
    """Get the OS name."""
    if platform.system() == "Linux":
        os_file = "/etc/os-release"
        if path.isfile(os_file):
            return (
                run_command(f"grep 'PRETTY_NAME' {os_file}")
                .replace("PRETTY_NAME=", "")
                .replace('"', "")
            )
    elif platform.system() == "Windows":
        return run_command("ver")  # Windows version command
    elif platform.system() == "Darwin":
        return run_command("sw_vers -productName")  # macOS version command
    return "Unknown OS"


def model_info():
    """Get model information."""
    if platform.system() == "Linux":
        product_info = run_command(
            "cat /sys/devices/virtual/dmi/id/product_name"
        ).strip()
        version_info = run_command(
            "cat /sys/devices/virtual/dmi/id/product_version"
        ).strip()
        return f"{product_info} {version_info}" if version_info else product_info
    elif platform.system() == "Windows":
        return run_command("wmic csproduct get name")  # Windows model command
    elif platform.system() == "Darwin":
        return run_command(
            "system_profiler SPHardwareDataType | awk '/Model Name:/ {print $3, $4}'"
        )
    return "Unknown model"


def fetch_cpu_info():
    """Fetch CPU information."""
    if platform.system() == "Linux":
        cpu_info = run_command(
            "cat /proc/cpuinfo | grep 'model name' | uniq | cut -d: -f2"
        )
        cpu_max_freq = (
            int(
                run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
            )
            / 1000
        )
        cpu_freq_info = (
            f"{cpu_max_freq:.3f} MHz"
            if cpu_max_freq < 1000
            else f"{cpu_max_freq / 1000:.3f} GHz"
        )
        return f"{cpu_info} @ {cpu_freq_info}"
    elif platform.system() == "Windows":
        return run_command("wmic cpu get name")  # Windows CPU command
    elif platform.system() == "Darwin":
        return run_command("sysctl -n machdep.cpu.brand_string")  # macOS CPU command
    return "Unknown CPU"


def gpu_info():
    """Fetch GPU information."""
    if platform.system() == "Darwin":
        return run_command(
            "system_profiler SPDisplaysDataType | awk '/Chipset Model:/ {print $3, $4, $5, $6, $7}'"
        ).strip()
    elif platform.system() == "Linux":
        return truncate_string(
            run_command("lspci | grep -i vga").split(":")[2].split("(")[0].strip(), 50
        )
    elif platform.system() == "Windows":
        return run_command(
            "wmic path win32_videocontroller get name"
        )  # Windows GPU command
    return "Unknown GPU"


def fetch_arch():
    """Fetch architecture information."""
    arch = platform.machine()
    return f"{arch}"
