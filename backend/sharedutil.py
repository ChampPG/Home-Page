##############################
#   Name: sharedutil.py
#   Description: Shared utility functions for the backend
#   Author: Paul Gleason
#   Date: 2025-06-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
#   Notes:
#   - Shared utility functions for the backend
##############################

from datetime import datetime
import json

# Log levels
LOG_LEVEL_DEBUG = 0
LOG_LEVEL_INFO = 1
LOG_LEVEL_WARN = 2
LOG_LEVEL_ERROR = 3

LOG_LEVEL = LOG_LEVEL_INFO

def stdlog(message: str, log_level: int = LOG_LEVEL_INFO):
    if LOG_LEVEL >= LOG_LEVEL_INFO:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def dblog(message: str, log_level: int = LOG_LEVEL_DEBUG):
    if LOG_LEVEL >= LOG_LEVEL_DEBUG:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def errlog(message: str, log_level: int = LOG_LEVEL_ERROR):
    if LOG_LEVEL >= LOG_LEVEL_ERROR:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def open_json_file(file_path: str) -> dict:
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        errlog(f"Error opening {file_path}: {e}")
        return {}
    
def write_json_file(file_path: str, data: dict):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        errlog(f"Error writing to {file_path}: {e}")
