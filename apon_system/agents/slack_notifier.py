import logging
import requests
from config import settings

logger = logging.getLogger('SlackNotifier')

SLACK_WEBHOOK = getattr(settings, 'SLACK_WEBHOOK', None)

def send_alert(message: str, channel: str = "#market-alerts") -> bool:
    """Send alert to Slack."""
    if not SLACK_WEBHOOK or SLACK_WEBHOOK == "your_slack_webhook_url":
        logger.warning("Slack webhook not configured - printing message instead")
        print(f"SLACK ALERT: {message}")
        return True
    try:
        payload = {
            "channel": channel,
            "username": "Apon Market Bot",
            "text": message,
            "icon_emoji": ":chart_with_upwards_trend:"
        }
        response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Successfully sent Slack alert")
            return True
        else:
            logger.error(f"Failed to send Slack alert: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error sending Slack alert: {e}")
        return False
