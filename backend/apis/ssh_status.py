##############################
#   Name: ssh_service.py
#   Description: Checks if SSH service is running
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
    Check if SSH service is running
    Expected format: hostname:port or ip:port
    Example: 192.168.0.1:22 or example.com:22
    """
    try:
        # Parse host and port from URL
        if ':' not in url:
            errlog(f"Invalid SSH URL format: {url}. Expected hostname:port or ip:port")
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
        
        return _check_ssh_connection(host, port)
        
    except Exception as e:
        errlog(f"Error checking SSH service {url}: {e}")
        return False

def _check_ssh_connection(host: str, port: int) -> bool:
    """
    Attempt to establish a connection and verify SSH service is responding
    """
    try:
        # Create socket with timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)  # 2 second timeout
        
        # Try to connect
        result = sock.connect_ex((host, port))
        if result != 0:
            sock.close()
            return False
        
        # Connection established, now verify SSH service is responding
        service_responding = _verify_ssh_service(sock)
        sock.close()
        
        return service_responding
        
    except Exception as e:
        errlog(f"SSH connection error to {host}:{port}: {e}")
        return False

def _verify_ssh_service(sock: socket.socket) -> bool:
    """Verify SSH service is responding"""
    try:
        # SSH sends a banner immediately upon connection
        response = sock.recv(1024)
        return b"SSH" in response
    except:
        return False 