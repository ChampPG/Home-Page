##############################
#   Name: app.py
#   Description: Main application file for the backend
#   Author: Paul Gleason
#   Date: 2025-06-14
#   Version: 1.0.0
#   License: MIT
#   Contact: paul@paulgleason.dev
#   Website: https://home.paulgleason.dev
#   GitHub: https://github.com/ChampPG
##############################

# Standard modules
from flask import Flask, jsonify, render_template, send_from_directory
import sqlite3
import threading
import time
from datetime import datetime, timezone, timedelta
import schedule
import os
import shutil

# Custom modules
import apis.autobrr_status, apis.flaresolverr_status, apis.host_status, apis.http_status, apis.nginx_status, apis.overseerr_status, apis.plex_status, apis.port_status, \
    apis.prowlarr_status, apis.qbit_status, apis.radarr_status, apis.sonarr_status, apis.ssh_status, apis.syncthing_status, apis.tautulli_status, apis.wireguard_status
from sharedutil import stdlog, dblog, errlog, open_json_file

app = Flask(__name__)

config = open_json_file("external/config.json")

# Global flag to prevent multiple schedulers
scheduler_running = False

def adapt_datetime(dt):
    """Convert datetime to ISO format string for SQLite"""
    return dt.isoformat()

def convert_datetime(s):
    """Convert ISO format string from SQLite to datetime"""
    if s is None:
        return None
    return datetime.fromisoformat(s)

def get_db_connection():
    """Get a database connection with proper datetime handling"""
    conn = sqlite3.connect("external/database/db.sqlite3", timeout=20.0)
    # Register adapters and converters for datetime handling
    sqlite3.register_adapter(datetime, adapt_datetime)
    sqlite3.register_converter("datetime", convert_datetime)
    return conn

def cleanup_old_backups():
    """Delete database backups that are over 2 weeks old"""
    try:
        backup_dir = "external/database"
        if not os.path.exists(backup_dir):
            return
            
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(weeks=2)
        
        deleted_count = 0
        for filename in os.listdir(backup_dir):
            if filename.startswith("db_backup_") and filename.endswith(".sqlite3"):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_time:
                    try:
                        os.remove(file_path)
                        stdlog(f"Deleted old backup: {filename}")
                        deleted_count += 1
                    except Exception as e:
                        errlog(f"Error deleting old backup {filename}: {e}")
        
        if deleted_count > 0:
            stdlog(f"Cleaned up {deleted_count} old backup files")
    except Exception as e:
        errlog(f"Error cleaning up old backups: {e}")

def backup_database():
    """Create a backup of the database if it exists"""
    db_path = "external/database/db.sqlite3"
    if os.path.exists(db_path):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = f"external/database/db_backup_{timestamp}.sqlite3"
        try:
            shutil.copy2(db_path, backup_path)
            stdlog(f"Database backed up to: {backup_path}")
            
            # Clean up old backups after creating a new one
            cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            errlog(f"Error backing up database: {e}")
            return None
    return None

def setup_db():
    # Sets up database in the external directory as external/database/db.sqlite3
    # This database will track services and their status and uptime
    
    # First, backup existing database if it exists
    backup_path = backup_database()
    
    # Ensure database directory exists
    db_dir = "external/database"
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
            stdlog(f"Created database directory: {db_dir}")
        except Exception as e:
            errlog(f"Error creating database directory: {e}")
            return
    
    # Remove existing database if it exists
    db_path = "external/database/db.sqlite3"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            stdlog("Removed existing database")
        except Exception as e:
            errlog(f"Error removing existing database: {e}")
            return
    
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Create new table with timestamp and downtime tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                response_time INTEGER,
                last_check DATETIME DEFAULT CURRENT_TIMESTAMP,
                consecutive_failures INTEGER
            )
        """)
        
        # Create table for downtime events
        c.execute("""
            CREATE TABLE IF NOT EXISTS downtime_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT,
                start_time DATETIME,
                end_time DATETIME,
                duration_minutes INTEGER,
                resolved BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.commit()
        conn.close()
        stdlog("New database created successfully")
    except Exception as e:
        errlog(f"Error setting up database: {e}")
        return


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
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get current status of all services
    c.execute("""
        SELECT name, status, timestamp, response_time, last_check, consecutive_failures
        FROM services 
        ORDER BY name
    """)
    services = c.fetchall()
    
    # Get downtime events for the last 24 hours
    c.execute("""
        SELECT service_name, start_time, end_time, duration_minutes, resolved
        FROM downtime_events 
        WHERE start_time >= datetime('now', '-24 hours')
        ORDER BY start_time DESC
    """)
    downtime_events = c.fetchall()
    
    conn.close()
    
    # Add category information and public URLs from config
    services_with_categories = []
    service_names_in_db = [service[0] for service in services]
    
    # First, add services from database
    for service in services:
        service_name = service[0]
        service_status = service[1]
        
        # Calculate actual uptime/downtime duration
        # Find when the service last changed status
        conn = get_db_connection()
        c = conn.cursor()
        
        # Find the first occurrence of current status that comes after a different status
        # This represents when the current status actually started
        c.execute("""
            SELECT MIN(timestamp) 
            FROM services 
            WHERE name = ? AND status = ?
            AND timestamp > (
                SELECT COALESCE(MAX(timestamp), '1970-01-01') 
                FROM services 
                WHERE name = ? AND status != ?
            )
        """, (service_name, service_status, service_name, service_status))
        
        status_start_result = c.fetchone()
        status_change_time = status_start_result[0] if status_start_result and status_start_result[0] else service[2]
        
        conn.close()
        
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
            "name": service[0],
            "status": service[1],
            "timestamp": service[2],
            "response_time": service[3],
            "last_check": service[4],
            "consecutive_failures": service[5],
            "status_since": status_change_time,  # When the current status started
            "category": category,
            "public_url": public_url,
            "type": service_type,
            "host": host,
            "ping_url": ping_url,
            "icon_url": icon_url
        })
    
    # Add services from config that aren't in the database (including hosts and redirects)
    for config_service in config[0]["instances"]:
        if config_service["name"] not in service_names_in_db:
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
    
    return jsonify({
        "services": services_with_categories,
        "downtime_events": downtime_events,
        "categories": config[0]["categories"]
    })


@app.route("/api/v1/services/history", methods=["GET"])
def get_service_history():
    """Get historical data for all services in the last 24 hours"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Get all service checks from the last 24 hours
        c.execute("""
            SELECT name, status, timestamp, response_time
            FROM services 
            WHERE timestamp >= datetime('now', '-24 hours')
            ORDER BY timestamp DESC
        """)
        history = c.fetchall()
        
        # Get downtime events for the last 24 hours
        c.execute("""
            SELECT service_name, start_time, end_time, duration_minutes, resolved
            FROM downtime_events 
            WHERE start_time >= datetime('now', '-24 hours')
            ORDER BY start_time DESC
        """)
        downtime_events = c.fetchall()
        
        conn.close()
        
        # Convert to list of dictionaries for easier frontend processing
        history_list = []
        for item in history:
            history_list.append({
                "name": item[0],
                "status": item[1],
                "timestamp": item[2],
                "response_time": item[3]
            })
        
        return jsonify({
            "history": history_list,
            "downtime_events": downtime_events
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
    """Check all services and update database with current status"""
    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
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
            
            # Insert current status with consecutive failures tracking
            c.execute("""
                INSERT INTO services (name, status, timestamp, response_time, last_check, consecutive_failures)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (service_name, "up" if status else "down", current_time, response_time, current_time, consecutive_failures))
            
            # Check for downtime events
            check_downtime_events(c, service_name, status, current_time)
            
            if status:
                print(f"{service_name}: UP (Response: {response_time}ms)")
            else:
                print(f"{service_name}: DOWN after {consecutive_failures} consecutive failures (Response: {response_time}ms)")
        
        conn.commit()
        print("Service check completed successfully")
    except Exception as e:
        print(f"Error checking services: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def check_downtime_events(cursor, service_name, current_status, current_time):
    """Track downtime events - when services go down and come back up"""
    
    try:
        # Get the last status for this service
        cursor.execute("""
            SELECT status, timestamp FROM services 
            WHERE name = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (service_name,))
        
        last_status_result = cursor.fetchone()
        
        if last_status_result:
            last_status = last_status_result[0]
            last_timestamp = last_status_result[1]
            
            # If service just went down
            if last_status == "up" and not current_status:
                # Service went down - create new downtime event
                cursor.execute("""
                    INSERT INTO downtime_events (service_name, start_time, end_time, duration_minutes, resolved)
                    VALUES (?, ?, NULL, NULL, FALSE)
                """, (service_name, current_time))
                print(f"🚨 {service_name} went DOWN at {current_time}")
            
            # If service just came back up
            elif last_status == "down" and current_status:
                # Calculate duration in minutes
                if isinstance(last_timestamp, str):
                    last_dt = datetime.fromisoformat(last_timestamp.replace('T', ' '))
                else:
                    last_dt = last_timestamp
                
                duration_minutes = int((current_time - last_dt).total_seconds() / 60)
                
                # Service came back up - update the latest unresolved downtime event
                cursor.execute("""
                    UPDATE downtime_events 
                    SET end_time = ?, duration_minutes = ?, resolved = TRUE
                    WHERE service_name = ? AND resolved = FALSE
                    ORDER BY start_time DESC
                    LIMIT 1
                """, (current_time, duration_minutes, service_name))
                print(f"✅ {service_name} came back UP at {current_time}")
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

    setup_db()
    check_services()

    # Start the scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    print("Scheduler started")
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    run_app()