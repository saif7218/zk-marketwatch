import os
from typing import Dict, Any

def send_telegram_alert(change_info: Dict[str, Any]) -> None:
    # Implement Telegram logic here (using python-telegram-bot).
    # Example:
    # bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    # chat_id = os.getenv("TELEGRAM_CHAT_ID")
    # if not bot_token or not chat_id:
    #     print("[Telegram Alert] Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set.")
    #     return
    # message = f"Price Monitor Alert!\nProduct: {change_info.get('product')}\nChange: {change_info.get('change_type')}\nOld: {change_info.get('old_value')}\nNew: {change_info.get('new_value')}\nURL: {change_info.get('url')}"
    # # ... send message using telegram bot library ...
    print(f"[Telegram Alert Placeholder] Change detected: {change_info.get('product')} - {change_info.get('change_type')}")
    pass

def send_slack_alert(change_info: Dict[str, Any]) -> None:
    # Implement Slack logic here (via webhook).
    # Example:
    # webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    # if not webhook_url:
    #     print("[Slack Alert] Error: SLACK_WEBHOOK_URL not set.")
    #     return
    # payload = {
    #     "text": f"Price Monitor Alert!\nProduct: {change_info.get('product')}\nChange: {change_info.get('change_type')}\nOld: {change_info.get('old_value')}\nNew: {change_info.get('new_value')}\nURL: {change_info.get('url')}"
    # }
    # # ... send POST request to webhook_url with payload ...
    print(f"[Slack Alert Placeholder] Change detected: {change_info.get('product')} - {change_info.get('change_type')}")
    pass

def send_console_alert(change_info: Dict[str, Any]) -> None:
    print(f"[!] CONSOLE ALERT: Product: {change_info.get('product')}")
    print(f"    Site: {change_info.get('site', 'N/A')}")
    change_type = change_info.get('change_type')
    print(f"    Change Type: {change_type}")
    
    old_value = change_info.get('old_value', 'N/A')
    new_value = change_info.get('new_value', 'N/A')

    if change_type == "price":
        print(f"    Old Price: {old_value}, New Price: {new_value}")
    elif change_type == "stock":
        print(f"    Old Stock Status (In Stock?): {old_value}, New Stock Status (In Stock?): {new_value}")
    elif change_type == "delivery_time":
        print(f"    Old Delivery: {old_value}, New Delivery: {new_value}")
    else: # Generic display for other change types
        print(f"    Old Value: {old_value}, New Value: {new_value}")
        
    print(f"    URL: {change_info.get('url', 'N/A')}")
    print(f"    Timestamp: {change_info.get('timestamp', 'N/A')}\n")

def send_alert(change_info: Dict[str, Any], method: str = "console") -> None:
    """
    Routes alerts to console, Telegram, or Slack based on `method`.
    """
    if method == "telegram":
        send_telegram_alert(change_info)
    elif method == "slack":
        send_slack_alert(change_info)
    elif method == "console":
        send_console_alert(change_info)
    else:
        print(f"[Alert System] Unknown alert method: '{method}'. Defaulting to console.")
        send_console_alert(change_info)
