##############################
#   Name: app.py
#   Description: Main application file for the backend
#   Author: Paul Gleason
#   Date: 2025-06-14
#   Version: 2.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
##############################

# Standard modules
from flask import Flask, jsonify, render_template, send_from_directory
import threading
import time
from datetime import datetime, timezone, timedelta
import schedule
import os
from collections import defaultdict, deque

# Custom modules
import apis.autobrr_status, apis.flaresolverr_status, apis.host_status, apis.http_status, apis.nginx_status, apis.overseerr_status, apis.plex_status, apis.port_status, \
    apis.prowlarr_status, apis.qbit_status, apis.radarr_status, apis.sonarr_status, apis.ssh_status, apis.syncthing_status, apis.tautulli_status, apis.wireguard_status
from sharedutil import stdlog, dblog, errlog, open_json_file

app = Flask(__name__)

config = open_json_file("external/config.json")

# Global flag to prevent multiple schedulers
scheduler_running = False

# In-memory storage for service data
# Structure: {service_name: deque(maxlen=50)} - stores latest 50 checks
service_checks = defaultdict(lambda: deque(maxlen=50))

# In-memory storage for downtime events
# Structure: list of downtime event dictionaries
downtime_events = []

def get_latest_service_status(service_name):
    """Get the latest status for a specific service"""
    if service_name in service_checks and service_checks[service_name]:
        return service_checks[service_name][-1]
    return None

def get_service_status_since(service_name, current_status):
    """Find when the current status started for a service"""
    if service_name not in service_checks:
        return None
    
    checks = list(service_checks[service_name])
    checks.reverse()  # Start from most recent
    
    for check in checks:
        if check['status'] != current_status:
            # Found the first different status, return the timestamp of the next check
            return check.get('timestamp')
    
    # If all checks have the same status, return the timestamp of the oldest check
    return checks[-1].get('timestamp') if checks else None

def add_service_check(service_name, status, response_time, consecutive_failures):
    """Add a new service check to the in-memory storage"""
    current_time = datetime.now(timezone.utc)
    
    check_data = {
        'name': service_name,
        'status': status,
        'timestamp': current_time.isoformat(),
        'response_time': response_time,
        'last_check': current_time.isoformat(),
        'consecutive_failures': consecutive_failures
    }
    
    service_checks[service_name].append(check_data)
    return check_data

def add_downtime_event(service_name, start_time, end_time=None, duration_minutes=None, resolved=False):
    """Add a downtime event to the in-memory storage"""
    event = {
        'service_name': service_name,
        'start_time': start_time.isoformat() if isinstance(start_time, datetime) else start_time,
        'end_time': end_time.isoformat() if isinstance(end_time, datetime) else end_time,
        'duration_minutes': duration_minutes,
        'resolved': resolved
    }
    
    downtime_events.append(event)
    
    # Keep only the last 100 downtime events
    if len(downtime_events) > 100:
        downtime_events.pop(0)

def get_recent_downtime_events(hours=24):
    """Get downtime events from the last specified hours"""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_events = []
    
    for event in downtime_events:
        try:
            event_time = datetime.fromisoformat(event['start_time'].replace('T', ' '))
            if event_time >= cutoff_time:
                recent_events.append(event)
        except:
            continue
    
    return recent_events

@app.route("/")
def index():
    frontend_path = '../frontend/dist'
    index_path = f'{frontend_path}/index.html'
    
    if not os.path.exists(frontend_path):
        return jsonify({"error": f"Frontend directory not found: {frontend_path}"}), 500
    
    if not os.path.exists(index_path):
        return jsonify({"error": f"Frontend index.html not found: {index_path}"}), 500
    
    return send_from_directory(frontend_path, 'index.html')

@app.route("/<path:path>")
def serve_frontend(path):
    frontend_path = '../frontend/dist'
    
    # Serve static files from the frontend dist directory
    if os.path.exists(f'{frontend_path}/{path}'):
        return send_from_directory(frontend_path, path)
    # For SPA routing, serve index.html for any non-API route
    elif not path.startswith('api/'):
        if os.path.exists(f'{frontend_path}/index.html'):
            return send_from_directory(frontend_path, 'index.html')
        else:
            return jsonify({"error": f"Frontend index.html not found: {frontend_path}/index.html"}), 500
    else:
        return jsonify({"error": "Not found"}), 404


@app.route("/api/v1/services", methods=["GET"])
def get_services():
    # Get current status of all services from in-memory storage
    services_with_categories = []
    service_names_in_storage = set(service_checks.keys())
    
    # First, add services from in-memory storage
    for service_name, checks in service_checks.items():
        if checks:  # Only process services that have checks
            latest_check = checks[-1]
            service_status = latest_check['status']
            
            # Calculate actual uptime/downtime duration
            status_since = get_service_status_since(service_name, service_status)
            
            # Find the service in config to get its category and public_url
            category = "unknown"
            public_url = ""
            service_type = "unknown"
            host = ""
            ping_url = ""
            icon_url = ""
            for config_service in config[0]["instances"]:
                if config_service["name"] == service_name:
                    category = config_service.get("category", "unknown")
                    public_url = config_service.get("public_url", "")
                    service_type = config_service.get("type", "unknown")
                    host = config_service.get("host", "")
                    ping_url = config_service.get("ping_url", "")
                    icon_url = config_service.get("icon_url", "")
                    break
            
            services_with_categories.append({
                "name": latest_check['name'],
                "status": latest_check['status'],
                "timestamp": latest_check['timestamp'],
                "response_time": latest_check['response_time'],
                "last_check": latest_check['last_check'],
                "consecutive_failures": latest_check['consecutive_failures'],
                "status_since": status_since,
                "category": category,
                "public_url": public_url,
                "type": service_type,
                "host": host,
                "ping_url": ping_url,
                "icon_url": icon_url
            })
    
    # Add services from config that aren't in the storage (including hosts and redirects)
    for config_service in config[0]["instances"]:
        if config_service["name"] not in service_names_in_storage:
            services_with_categories.append({
                "name": config_service["name"],
                "status": "unknown" if config_service["type"] == "host" else "redirect",
                "timestamp": None,
                "response_time": None,
                "last_check": None,
                "consecutive_failures": None,
                "status_since": None,
                "category": config_service.get("category", "unknown"),
                "public_url": config_service.get("public_url", ""),
                "type": config_service.get("type", "unknown"),
                "host": config_service.get("host", ""),
                "ping_url": config_service.get("ping_url", ""),
                "icon_url": config_service.get("icon_url", "")
            })
    
    # Get recent downtime events
    recent_downtime_events = get_recent_downtime_events(24)
    
    return jsonify({
        "services": services_with_categories,
        "downtime_events": recent_downtime_events,
        "categories": config[0]["categories"],
        "interval": config[0]["interval"]
    })


@app.route("/api/v1/services/history", methods=["GET"])
def get_service_history():
    """Get historical data for all services in the last 24 hours"""
    try:
        # Get all service checks from the last 24 hours
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
        history_list = []
        
        for service_name, checks in service_checks.items():
            for check in checks:
                try:
                    check_time = datetime.fromisoformat(check['timestamp'].replace('T', ' '))
                    if check_time >= cutoff_time:
                        history_list.append({
                            "name": check['name'],
                            "status": check['status'],
                            "timestamp": check['timestamp'],
                            "response_time": check['response_time']
                        })
                except:
                    continue
        
        # Sort by timestamp descending
        history_list.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Get recent downtime events
        recent_downtime_events = get_recent_downtime_events(24)
        
        return jsonify({
            "history": history_list,
            "downtime_events": recent_downtime_events
        })
    except Exception as e:
        errlog(f"Error getting service history: {e}")
        return jsonify({"error": "Error getting service history"}), 500


def check_service_with_retries(service_name, service_type, ping_url, max_failures=3):
    """Check a service multiple times before determining if it's down"""
    failures = 0
    total_response_time = 0
    check_count = 0
    
    for attempt in range(max_failures):
        try:
            start_time = time.time()
            name = service_type.lower()
            api = getattr(apis, f"{name}_status")
            status = api.get_status(ping_url)
            response_time = int((time.time() - start_time) * 1000)
            
            total_response_time += response_time
            check_count += 1
            
            if status:
                # Service is up, return immediately
                avg_response_time = total_response_time // check_count
                return True, avg_response_time, 0  # Reset consecutive failures
            
            failures += 1
            
            # If this isn't the last attempt, wait a bit before retrying
            if attempt < max_failures - 1:
                time.sleep(1)  # Wait 1 second between retries
                
        except Exception as e:
            failures += 1
            errlog(f"Error checking {service_name} (attempt {attempt + 1}): {e}")
            if attempt < max_failures - 1:
                time.sleep(1)
    
    # Service failed all checks
    avg_response_time = total_response_time // check_count if check_count > 0 else None
    return False, avg_response_time, failures

def check_services():
    """Check all services and update in-memory storage with current status"""
    try:
        current_time = datetime.now(timezone.utc)
        
        for service in config[0]["instances"]:
            service_name = service["name"]
            service_type = service["type"]
            
            # Skip redirect services (they don't have ping_url)
            if service_type == "redirect" or not service.get("ping_url"):
                continue
                
            # Check service with retries
            status, response_time, consecutive_failures = check_service_with_retries(
                service_name, service_type, service["ping_url"]
            )
            
            # Get previous status for downtime tracking
            previous_check = get_latest_service_status(service_name)
            previous_status = previous_check['status'] if previous_check else None
            
            # Add current status to in-memory storage
            add_service_check(service_name, "up" if status else "down", response_time, consecutive_failures)
            
            # Check for downtime events
            check_downtime_events(service_name, previous_status, "up" if status else "down", current_time)
            
            if status:
                print(f"{service_name}: UP (Response: {response_time}ms)")
            else:
                print(f"{service_name}: DOWN after {consecutive_failures} consecutive failures (Response: {response_time}ms)")
        
        print("Service check completed successfully")
    except Exception as e:
        print(f"Error checking services: {e}")


def check_downtime_events(service_name, previous_status, current_status, current_time):
    """Track downtime events - when services go down and come back up"""
    
    try:
        # If service just went down
        if previous_status == "up" and current_status == "down":
            # Service went down - create new downtime event
            add_downtime_event(service_name, current_time)
            print(f"🚨 {service_name} went DOWN at {current_time}")
        
        # If service just came back up
        elif previous_status == "down" and current_status == "up":
            # Find the latest unresolved downtime event for this service
            for event in reversed(downtime_events):
                if event['service_name'] == service_name and not event['resolved']:
                    # Calculate duration in minutes
                    try:
                        start_time = datetime.fromisoformat(event['start_time'].replace('T', ' '))
                        duration_minutes = int((current_time - start_time).total_seconds() / 60)
                        
                        # Update the event
                        event['end_time'] = current_time.isoformat()
                        event['duration_minutes'] = duration_minutes
                        event['resolved'] = True
                        
                        print(f"✅ {service_name} came back UP at {current_time}")
                        break
                    except:
                        continue
    except Exception as e:
        print(f"Error checking downtime events for {service_name}: {e}")


def run_scheduler():
    """Run the scheduler in a separate thread"""
    # Set up the schedule once - don't add it in the loop
    schedule.every(config[0]["interval"]).seconds.do(check_services)
    print(f"Scheduler configured to run every {config[0]['interval']} seconds")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"Scheduler error: {e}")
            time.sleep(5)  # Wait before retrying
            continue

def run_app():
    global scheduler_running
    
    # Prevent multiple schedulers from running
    if scheduler_running:
        print("Scheduler already running, skipping...")
        return
        
    scheduler_running = True

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Initialize with first service check
    # check_services()

    print("Scheduler started")
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_app()