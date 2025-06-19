##############################
#   Name: port_status.py
#   Description: Checks if a service is running on a port
#   Author: Paul Gleason
#   Date: 2025-01-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
#   Notes:
#   - Checks if a service is actually running and responding on a port
#   - Attempts to establish a connection and verify service response
##############################

import socket
import struct
from sharedutil import errlog

def get_status(url: str) -> bool:
    """
    Check if a service is running on a port
    Expected format: hostname:port or ip:port
    Example: 192.168.0.1:32400 or example.com:8080
    
    This function attempts to:
    1. Establish a TCP connection
    2. Send a basic probe to verify the service responds
    3. Handle common service types (HTTP, SSH, etc.)
    """
    try:
        # Parse host and port from URL
        if ':' not in url:
            errlog(f"Invalid port URL format: {url}. Expected hostname:port or ip:port")
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
        
        # print(f"Checking service on {host}:{port}")
        
        # Try to establish a connection and verify service response
        return _check_service_connection(host, port)
        
    except Exception as e:
        errlog(f"Error checking port {url}: {e}")
        return False

def _check_service_connection(host: str, port: int) -> bool:
    """
    Attempt to establish a connection and verify the service is responding
    """
    try:
        # Create socket with timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)  # 2 second timeout for service verification
        
        # Try to connect
        result = sock.connect_ex((host, port))
        if result != 0:
            sock.close()
            return False
        
        # Connection established, now verify service is responding
        service_responding = _verify_service_response(sock, port)
        sock.close()
        
        return service_responding
        
    except Exception as e:
        errlog(f"Connection error to {host}:{port}: {e}")
        return False

def _verify_service_response(sock: socket.socket, port: int) -> bool:
    """
    Verify that a service is actually responding on the connected socket
    """
    try:
        # Common service verification based on port
        if port in [80, 8080, 3000, 5000, 8000, 9000]:  # HTTP-like services
            return _verify_http_service(sock)
        elif port == 22:  # SSH
            return _verify_ssh_service(sock)
        elif port == 21:  # FTP
            return _verify_ftp_service(sock)
        elif port == 25:  # SMTP
            return _verify_smtp_service(sock)
        elif port == 143:  # IMAP
            return _verify_imap_service(sock)
        elif port == 110:  # POP3
            return _verify_pop3_service(sock)
        elif port == 53:  # DNS
            return _verify_dns_service(sock)
        elif port == 51820:  # WireGuard
            return _verify_wireguard_service(sock)
        elif port == 22067:  # Syncthing
            return _verify_syncthing_service(sock)
        else:
            # For unknown ports, try a basic probe
            return _verify_generic_service(sock)
            
    except Exception as e:
        errlog(f"Service verification error on port {port}: {e}")
        return False

def _verify_http_service(sock: socket.socket) -> bool:
    """Verify HTTP service is responding"""
    try:
        # Send a simple HTTP HEAD request
        request = b"HEAD / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        sock.send(request)
        
        # Wait for response
        response = sock.recv(1024)
        return b"HTTP/" in response and (b"200" in response or b"404" in response or b"403" in response)
    except:
        return False

def _verify_ssh_service(sock: socket.socket) -> bool:
    """Verify SSH service is responding"""
    try:
        # SSH sends a banner immediately upon connection
        response = sock.recv(1024)
        return b"SSH" in response
    except:
        return False

def _verify_ftp_service(sock: socket.socket) -> bool:
    """Verify FTP service is responding"""
    try:
        response = sock.recv(1024)
        return b"220" in response and b"FTP" in response
    except:
        return False

def _verify_smtp_service(sock: socket.socket) -> bool:
    """Verify SMTP service is responding"""
    try:
        response = sock.recv(1024)
        return b"220" in response and b"SMTP" in response
    except:
        return False

def _verify_imap_service(sock: socket.socket) -> bool:
    """Verify IMAP service is responding"""
    try:
        response = sock.recv(1024)
        return b"* OK" in response or b"* PREAUTH" in response
    except:
        return False

def _verify_pop3_service(sock: socket.socket) -> bool:
    """Verify POP3 service is responding"""
    try:
        response = sock.recv(1024)
        return b"+OK" in response
    except:
        return False

def _verify_dns_service(sock: socket.socket) -> bool:
    """Verify DNS service is responding"""
    try:
        # Send a simple DNS query
        query = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0) + b"\x07example\x03com\x00" + struct.pack("!HH", 1, 1)
        sock.send(query)
        
        response = sock.recv(1024)
        return len(response) > 0
    except:
        return False

def _verify_wireguard_service(sock: socket.socket) -> bool:
    """Verify WireGuard service is responding"""
    try:
        # WireGuard typically doesn't respond to TCP, but we can check if it's listening
        # For WireGuard, just having the port open usually means the service is running
        return True
    except:
        return False

def _verify_syncthing_service(sock: socket.socket) -> bool:
    """Verify Syncthing service is responding"""
    try:
        # Syncthing typically responds to HTTP requests on this port
        request = b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"
        sock.send(request)
        
        response = sock.recv(1024)
        return b"HTTP/" in response
    except:
        return False

def _verify_generic_service(sock: socket.socket) -> bool:
    """Generic service verification for unknown ports"""
    try:
        # Try to send a small probe and see if we get any response
        probe = b"\x00\x00\x00\x00"  # Null probe
        sock.send(probe)
        
        # Set a short timeout for the response
        sock.settimeout(1.0)
        response = sock.recv(1024)
        
        # If we get any response, the service is likely running
        return len(response) > 0
    except socket.timeout:
        # No response within timeout, but connection was established
        # This might indicate a service that doesn't respond to our probe
        # but is still running (like some game servers, custom protocols, etc.)
        return True
    except:
        return False