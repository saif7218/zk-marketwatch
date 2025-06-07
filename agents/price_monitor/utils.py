import os
import json
from datetime import datetime

SNAPSHOTS_DIR = "snapshots"

def store_snapshot(site_name, data):
    """Stores scraped data as a JSON snapshot with timestamp"""
    # Ensure directory structure exists
    site_dir = os.path.join(SNAPSHOTS_DIR, site_name)
    os.makedirs(site_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}.json"
    filepath = os.path.join(site_dir, filename)
    
    # Save data as JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[Utils] Saved snapshot: {filepath}")
    return timestamp

# TODO: Add database integration options:
# - Supabase: Use supabase-py
# - Google Sheets: Use gspread
# - SQLite: Built-in
