import logging
import os
from logging.config import dictConfig

from flask import Flask

home_dir = os.path.expanduser("~")
log_file_path = os.path.join(home_dir, "logs/SDashPanel.log")

app = Flask(__name__)

app_version = "0.3.6"


logging.basicConfig(
    encoding="utf-8",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(threadName)s : %(message)s",
    handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()],
)
