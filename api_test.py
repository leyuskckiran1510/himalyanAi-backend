#!/usr/bin/env python3
import requests
import json
import time
import os
import sqlite3
from pprint import pprint

# Configuration
BASE_URL = "http://localhost:5000/api"
ANON_HASH = "test_user_hash_123"

def check_db_status():
    """Check if the database exists and has tables"""
    print("\n=== Checking Database Status ===")
    
    # Check if database file exists
    if not os.path.exists("data.db"):
        print("❌ Database file 'data.db' does not exist!")
        return False
    
    # Check if database has tables
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ Database exists but has no tables!")
            return False
        
        print("✅ Database exists with tables:", [table[0] for table in tables])
        
        # Check if tables have data
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"   - Table '{table[0]}' has {count} records")
        
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False

def initialize_db():
    """Initialize the database by running the Flask app with db.create_all()"""
    print("\n=== Initializing Database ===")
    
    try:
        # Import Flask app and initialize database
        from app import create_app, db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def authenticate_user():
    """Authenticate or create a user and return the access token"""
    print("\n=== Authenticating User ===")
    
    try:
        response = requests.post(
            f"{BASE_URL}/authenticate_or_identify",
            json={"hash": ANON_HASH}
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ User authenticated successfully")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return None

def test_summarize(token):
    """Test the summarize endpoint"""
    print("\n=== Testing Summarize Endpoint ===")
    
    if not token:
        print("❌ Cannot test summarize without authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Sample content to summarize
    data = {
        "content": "This is a test content for summarization. The Flask application should process this text and generate a summary.",
        "url": "example.com",
        "full": "https://example.com/test-page"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/summarize",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Summarize request successful")
            print("Summary response:")
            pprint(response.json())
            return True
        else:
            print(f"❌ Summarize request failed: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def check_user_history(token):
    """Check if user history is being saved"""
    print("\n=== Checking User History ===")
    
    if not token:
        print("❌ Cannot check history without authentication token")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/fetch_user_history",
            headers=headers
        )
        
        if response.status_code == 200:
            history = response.json()
            if history:
                print(f"✅ User has {len(history)} history entries")
                print("History data:")
                pprint(history)
            else:
                print("⚠️ User history is empty")
            return True
        else:
            print(f"❌ History request failed: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def check_db_health():
    """Check database health using the db_health endpoint"""
    print("\n=== Checking Database Health ===")
    
    try:
        response = requests.get(f"{BASE_URL}/db_health")
        
        if response.status_code == 200:
            health_data = response.json()
            print("Database health:")
            pprint(health_data)
            return health_data.get("status") == "healthy"
        else:
            print(f"❌ DB health check failed: {response.status_code} - {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    print("=== API Testing Script ===")
    
    # Check if Flask server is running
    try:
        response = requests.get("http://localhost:5000/")
        print(f"✅ Flask server is running")
    except requests.ConnectionError:
        print("❌ Flask server is not running. Please start it with 'python run.py'")
        choice = input("Do you want to start the Flask server now? (y/n): ")
        if choice.lower() == 'y':
            import subprocess
            import threading
            
            def run_flask():
                subprocess.run(["python", "run.py"])
            
            flask_thread = threading.Thread(target=run_flask)
            flask_thread.daemon = True
            flask_thread.start()
            print("⏳ Starting Flask server... waiting 5 seconds")
            time.sleep(5)
        else:
            return
    
    # Check database status
    db_ok = check_db_status()
    
    # Initialize database if needed
    if not db_ok:
        initialize_db()
        db_ok = check_db_status()
    
    # Check database health
    db_health = check_db_health()
    
    # Authenticate user
    token = authenticate_user()
    
    if token:
        # Test summarize endpoint
        summarize_ok = test_summarize(token)
        
        # Wait a bit for background thread to complete
        if summarize_ok:
            print("⏳ Waiting for background processing to complete...")
            time.sleep(3)
        
        # Check user history
        history_ok = check_user_history(token)
        
        # Final database check
        final_db_check = check_db_status()
        
        # Summary
        print("\n=== Test Summary ===")
        print(f"Database Status: {'✅' if final_db_check else '❌'}")
        print(f"Database Health: {'✅' if db_health else '❌'}")
        print(f"Authentication: {'✅' if token else '❌'}")
        print(f"Summarize API: {'✅' if summarize_ok else '❌'}")
        print(f"User History: {'✅' if history_ok else '❌'}")

if __name__ == "__main__":
    main()
