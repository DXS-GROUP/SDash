import os
import platform
import subprocess
import time

import psutil
from config import dictConfig
from flask import Flask, jsonify, render_template, request
from get_info import (fetch_cpu_info, get_ip_address, get_uptime, gpu_info,
                      model_info, os_name)
from routes import app
from setproctitle import getproctitle, setproctitle

if __name__ == "__main__":
    setproctitle("SDash")
    app.logger.warning("!!! New User logging in")
    app.run(debug=True, host=get_ip_address())
