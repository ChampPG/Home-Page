##############################
#   Name: http_status.py
#   Description: Checks the status of the HTTP server
#   Author: Paul Gleason
#   Date: 2025-06-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
#   Notes:
#   - Very basic request call to check if the server is up. DON"T ACTUALLY CHECK IF SERVICE IS PROPERLY RUNNING.
##############################

import requests
from sharedutil import errlog

def get_status(url: str) -> int:
    try:
        response = requests.get(url, timeout=0.03)  # 30ms timeout
        if response.status_code != 200:
            return False
        return True
    except Exception as e:
        errlog(f"Error checking {url}: {e}")
        return False
    
# def main():
#     urls = ["https://play.default.dance", "https://qbit.leahy.center", "https://nzbget.leahy.center", "http://10.20.0.84:32400"]
#     for url in urls:
#         code = get_http_status(url)
#         print(f"{url}: {code}")

# if __name__ == "__main__":
#     main()