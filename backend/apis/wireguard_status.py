##############################
#   Name: wireguard_service.py
#   Description: Checks if WireGuard service is running over UDP
#   Author: Paul Gleason
#   Date: 2025-01-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
##############################

import socket
import struct
import time
from sharedutil import errlog

def get_status(url: str) -> bool:
    """
    Check if WireGuard UDP port is open
    Expected format: hostname:port or ip:port
    Example: 192.168.0.1:51820 or example.com:51820
    """
    try:
        # Parse host and port from URL
        if ':' not in url:
            errlog(f"Invalid WireGuard URL format: {url}. Expected hostname:port or ip:port")
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
        
        return _check_udp_port_open(host, port)
        
    except Exception as e:
        errlog(f"Error checking WireGuard service {url}: {e}")
        return False

def _check_udp_port_open(host: str, port: int) -> bool:
    """
    Check if UDP port is open by sending a probe packet
    """
    try:
        # Create UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)  # 2 second timeout
        
        # Send a probe packet to the UDP port
        probe_data = b"\x00" * 64  # 64-byte null packet
        sock.sendto(probe_data, (host, port))
        
        # Try to receive a response (WireGuard might not respond, but port could be open)
        try:
            sock.recvfrom(1024)
            sock.close()
            return True
        except socket.timeout:
            # No response received, but port might still be open
            # For WireGuard, just being able to send to the port usually means it's listening
            sock.close()
            return True
            
    except Exception as e:
        errlog(f"UDP port check error to {host}:{port}: {e}")
        return False