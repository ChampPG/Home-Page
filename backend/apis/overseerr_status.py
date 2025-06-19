##############################
#   Name: overseerr_status.py
#   Description: Checks the status of the Overseerr server
#   Author: Paul Gleason
#   Date: 2025-06-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
##############################

import requests
from sharedutil import errlog

def get_status(url: str) -> int:
    try:
        response = requests.get(url, timeout=0.03)
        if response.status_code != 200:
            return False
        return True
    except Exception as e:
        errlog(f"Error checking {url}: {e}")
        return False