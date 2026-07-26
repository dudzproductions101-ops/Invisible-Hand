# logs.py

import logging
import os
import uuid

LOG_FILE = "logs.txt"
LOG_LEVEL = logging.INFO
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

SESSION_ID = str(uuid.uuid4())

logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format=FORMAT,
    datefmt=DATE_FORMAT
)


def log(message: str, level: str = "info"):
    msg = f"[session={SESSION_ID}] {message}"
    level = level.lower()
    if level == "debug":
        logging.debug(msg)
    elif level == "warning":
        logging.warning(msg)
    elif level == "error":
        logging.error(msg)
    elif level == "critical":
        logging.critical(msg)
    else:
        logging.info(msg)


def show_logs() -> str:
    if not os.path.exists(LOG_FILE):
        return "Log file not found."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        return content if content else "Log file is empty."


def clear_logs() -> str:
    try:
        open(LOG_FILE, "w").close()
        return "Logs cleared."
    except Exception as e:
        return f"Error clearing logs: {e}"
