##############################
#   Name: host_status.py
#   Description: Checks if a host is online by pinging it
#   Author: Paul Gleason
#   Date: 2025-01-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
#   Notes:
#   - Uses ping to check if a host is online
##############################

import subprocess
import platform
from sharedutil import errlog

def get_status(url: str) -> bool:
    """
    Check if a host is online by pinging it
    Expected format: hostname or ip address
    Example: 192.168.1.1 or example.com
    """
    try:
        # Parse host from URL
        host = url.strip()
        
        # Remove http:// or https:// if present
        if host.startswith('http://'):
            host = host[7:]
        elif host.startswith('https://'):
            host = host[8:]
        
        # Remove port if present (for ping we only need the host)
        if ':' in host:
            host = host.split(':')[0]
        
        # Determine ping command based on OS
        if platform.system().lower() == "windows":
            ping_cmd = ["ping", "-n", "1", "-w", "1000", host]  # Windows: 1 ping, 1 second timeout
        else:
            ping_cmd = ["ping", "-c", "1", "-W", "1", host]  # Linux/Mac: 1 ping, 1 second timeout
        
        # Execute ping command
        result = subprocess.run(ping_cmd, capture_output=True, text=True, timeout=2)
        
        # Check if ping was successful
        # Return code 0 means success on most systems
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        errlog(f"Ping timeout for {url}")
        return False
    except Exception as e:
        errlog(f"Error pinging {url}: {e}")
        return False
