import platform
import socket
import sys
import time
from logging import info
from os import environ
from os.path import exists, isfile
from subprocess import DEVNULL, PIPE, Popen

import psutil


def get_uptime():
    if platform.system() == "Linux":
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.readline().split()[0])
    else:
        return "Error."

    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    return f"{int(days)} d. {int(hours)} h. {int(minutes)} m. {int(seconds)} s."


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def run_command(command):
    process = Popen(
        command, stdout=PIPE, universal_newlines=True, shell=True, stderr=DEVNULL
    )
    stdout, stderr = process.communicate()
    del stderr
    return stdout


def os_name():
    if isfile("/bedrock/etc/os-release"):
        os_file = "/bedrock/etc/os-release"
    elif isfile("/etc/os-release"):
        os_file = "/etc/os-release"

    pretty_name = (
        run_command(("cat " + os_file + " | grep 'PRETTY_NAME'"))
        .replace("PRETTY_NAME=", "")
        .replace('''"''', "")
    )
    return pretty_name


def model_info():
    product_info = ""
    if exists("/sys/devices/virtual/dmi/id/product_name"):
        with open("/sys/devices/virtual/dmi/id/product_name", "r") as f:
            line = f.read().rstrip("\n")
            product_info = line

    if exists("/sys/devices/virtual/dmi/id/product_version"):
        line = run_command("cat /sys/devices/virtual/dmi/id/product_version").rstrip(
            "\n"
        )
        if product_info == "":
            product_info = line
        else:
            product_info = str(product_info + " " + line)
    return product_info


def fetch_cpu_info():
    cpu_count = len(run_command("ls /sys/class/cpuid/ | sort").split("\n")) - 1
    cpu_info = (
        run_command("cat /proc/cpuinfo | grep 'model name'")
        .split("\n")[0]
        .replace("model name	: ", "")
        .replace("Core(TM)", "")
        .replace("(R)", "")
        .replace("CPU", "")
        .replace("  ", " ")
        .split("@")[0]
    )
    cpu_max_freq = int(
        run_command("cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
    )

    cpu_max_freq_mhz = cpu_max_freq / 1000
    cpu_max_freq_ghz = cpu_max_freq / 1000 / 1000

    if cpu_max_freq_ghz > 1:
        cpu_freq_info = str(str(round(cpu_max_freq_ghz, 3)) + "GHz")
    else:
        cpu_freq_info = str(str(round(cpu_max_freq_mhz, 3)) + "MHz")

    full_cpu_info = f"{cpu_info}({cpu_count}) @ {cpu_freq_info}"
    del cpu_freq_info, cpu_count, cpu_info, cpu_max_freq_mhz, cpu_max_freq_ghz
    return full_cpu_info


def gpu_info():
    if sys.platform == "darwin":  # Check for macOS
        gpu_info = run_command(
            "system_profiler SPDisplaysDataType | awk '/Chipset Model:/ {print $3, $4, $5, $6, $7}'"
        )
        return gpu_info.strip()
    else:
        gpu_info = ""
        if exists("/sys/class/dmi/id/product_name"):
            gpu_info = (
                run_command("lspci | grep -i vga").split(":")[2].split("(")[0].strip()
            )
        else:
            pass

        return gpu_info
