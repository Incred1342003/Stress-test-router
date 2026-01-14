import logging
import os
from colorlog import ColoredFormatter

# Ensure the directory exists
LOG_DIR = "results/realtime_log"
os.makedirs(LOG_DIR, exist_ok=True)

# Define the global logger
logger = logging.getLogger("network_test")
logger.setLevel(logging.INFO)
logger.handlers = []  # Start clean

# --- Console Handler (Immediate Output) ---
console_handler = logging.StreamHandler()
console_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)-8s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "white",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# --- File Handler Trigger ---


def add_version_specific_file_handler(router_version):
    """
    Called by environment.py to start recording to a specific file.
    Example: results/realtime_log/Router_6E_report.log
    """
    file_path = os.path.join(LOG_DIR, f"{router_version}_report.log")

    # Overwrite the log file if it already exists for this version
    if os.path.exists(file_path):
        os.remove(file_path)

    # Setup the file recorder
    file_handler = logging.FileHandler(file_path)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
