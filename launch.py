import subprocess
import sys
import webbrowser
from pathlib import Path
import time
import signal
import os

def start_backend():
    """Start the FastAPI backend server"""
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "price-monitor.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def start_monitoring():
    """Start the price monitoring service"""
    return subprocess.Popen(
        [sys.executable, "price-monitor/scraper.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def main():
    print("🚀 Starting Apon Price Monitor")
    
    processes = []
    try:
        # Start backend
        print("Starting backend server...")
        backend = start_backend()
        processes.append(backend)
        time.sleep(2)  # Wait for backend to start
        
        # Start monitoring service
        print("Starting price monitor...")
        monitor = start_monitoring()
        processes.append(monitor)
        
        # Open web interface
        print("Opening web interface...")
        webbrowser.open("http://localhost:8000")
        
        print("\n✨ System started!")
        print("Press Ctrl+C to stop")
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        for p in processes:
            if sys.platform == 'win32':
                p.kill()
            else:
                p.send_signal(signal.SIGTERM)
        print("Goodbye!")

if __name__ == "__main__":
    main()
