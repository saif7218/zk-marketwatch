import os
import time
from .scraper import scrape_product_data
from .tracker import detect_changes
from .alert import send_alert
from .utils import store_snapshot

# Default monitoring interval if not set by environment variable
DEFAULT_MONITOR_INTERVAL = 600  # seconds (10 minutes)

def run_agent(target_url: str, alert_method: str, monitor_interval: int):
    print(f"[Agent] Starting Apon rival monitor for URL: {target_url}")
    print(f"[Agent] Alert method: {alert_method}, Monitoring interval: {monitor_interval}s")

    if not target_url:
        print("[Agent] Error: TARGET_URL is not set. Agent cannot start.")
        return

    while True:
        print(f"--- Agent Cycle Start ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
        print(f"[Agent] Scraping competitor data from {target_url}...")
        current_data = scrape_product_data(target_url)

        if not current_data:
            print("[Agent] No data scraped. Skipping rest of the cycle.")
        else:
            print(f"[Agent] Scraped {len(current_data)} items. Storing snapshot...")
            # Assuming site name can be derived or is fixed for the target_url context
            # For simplicity, using "competitor" as the site name for snapshot storage
            store_snapshot("competitor", current_data)

            print("[Agent] Detecting changes...")
            # The 'site' parameter for detect_changes matches the one used for store_snapshot
            result = detect_changes(current_data, site="competitor")
            changes = result.get("changes", []) # Ensure changes is always a list

            if result.get("changes_detected"):
                print(f"[Agent] {len(changes)} change(s) detected. Processing...")
                for change in changes:
                    # Ensure the 'change' dictionary has all necessary info for alerts
                    # The updated tracker.py should provide this.
                    send_alert(change, method=alert_method)
            else:
                print("[Agent] No changes detected.")
        
        print(f"[Agent] Cycle finished. Waiting for {monitor_interval} seconds...")
        print("--- Agent Cycle End ---")
        time.sleep(monitor_interval)

if __name__ == "__main__":
    print("[Agent Main] Initializing agent...")
    
    target_url = os.getenv("TARGET_URL")
    if not target_url:
        print("[Agent Main] CRITICAL: TARGET_URL environment variable not set. Exiting.")
        exit(1)
        
    alert_method = os.getenv("ALERT_METHOD", "console")
    
    try:
        monitor_interval_str = os.getenv("MONITOR_INTERVAL", str(DEFAULT_MONITOR_INTERVAL))
        monitor_interval = int(monitor_interval_str)
        if monitor_interval <= 0:
            print(f"[Agent Main] MONITOR_INTERVAL must be positive. Using default: {DEFAULT_MONITOR_INTERVAL}s")
            monitor_interval = DEFAULT_MONITOR_INTERVAL
    except ValueError:
        print(f"[Agent Main] Invalid MONITOR_INTERVAL value. Using default: {DEFAULT_MONITOR_INTERVAL}s")
        monitor_interval = DEFAULT_MONITOR_INTERVAL

    run_agent(
        target_url=target_url,
        alert_method=alert_method,
        monitor_interval=monitor_interval
    )
