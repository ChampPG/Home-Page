##############################
#   Name: syncthing_service.py
#   Description: Checks if Syncthing service is running
#   Author: Paul Gleason
#   Date: 2025-01-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
##############################

import socket
from sharedutil import errlog

def get_status(url: str) -> bool:
    """
    Check if Syncthing relay service is running on the given host:port.
    Expected format: hostname:port or ip:port
    Example: 192.168.0.1:22067 or example.com:22067
    """
    try:
        # Parse host and port from URL
        if ':' not in url:
            errlog(f"Invalid Syncthing URL format: {url}. Expected hostname:port or ip:port")
            return False
        host, port_str = url.split(':', 1)
        # Remove http:// or https:// if present
        if host.startswith('http://'):
            host = host[7:]
        elif host.startswith('https://'):
            host = host[8:]
        # Convert port to integer
        try:
            port = int(port_str)
        except ValueError:
            errlog(f"Invalid port number: {port_str}")
            return False
        return _check_syncthing_connection(host, port)
    except Exception as e:
        errlog(f"Error checking Syncthing service {url}: {e}")
        return False

def _check_syncthing_connection(host: str, port: int) -> bool:
    """
    Attempt to establish a TCP connection to the Syncthing relay port.
    Return True if connection is successful, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=2.0):
            return True
    except Exception as e:
        errlog(f"Syncthing connection error to {host}:{port}: {e}")
        return False