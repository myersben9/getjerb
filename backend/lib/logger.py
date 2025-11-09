import logging
import os
from logging.handlers import RotatingFileHandler

# Directory for log files
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Full path to log file
LOG_FILE = os.path.join(LOG_DIR, "jobbot.log")

# Configure main logger
logger = logging.getLogger("JobBot")
logger.setLevel(logging.DEBUG)  # can adjust to INFO in production

# Formatter with timestamps and module names
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

# File handler (rotates after 5MB)
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

# Console handler (optional — for local dev, not production)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# Add handlers if not already added
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
