import logging
import os
from logging.config import dictConfig

from flask import Flask

home_dir = os.path.expanduser("~")
log_file_path = os.path.join(home_dir, "logs/ServerPanel.log")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
        },
    }
)
