import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('notifications.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class NotificationConfig:
    """Configuration for notification services"""
    email_enabled: bool = False
    email_sender: str = ""
    email_password: str = ""
    email_recipients: List[str] = field(default_factory=list)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    webhook_enabled: bool = False
    webhook_url: str = ""
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            email_enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
            email_sender=os.getenv("EMAIL_SENDER", ""),
            email_password=os.getenv("EMAIL_PASSWORD", ""),
            email_recipients=os.getenv("EMAIL_RECIPIENTS", "").split(","),
            smtp_server=os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            
            telegram_enabled=os.getenv("TELEGRAM_ENABLED", "false").lower() == "true",
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            
            webhook_enabled=os.getenv("WEBHOOK_ENABLED", "false").lower() == "true",
            webhook_url=os.getenv("WEBHOOK_URL", "")
        )

class NotificationService:
    """Service for sending notifications about price changes"""
    
    def __init__(self, config: Optional[NotificationConfig] = None):
        self.config = config or NotificationConfig.from_env()
    
    def send_notification(self, title: str, message: str, data: Optional[Dict] = None):
        """Send notification through all enabled channels"""
        data = data or {}
        
        # Prepare the full message
        full_message = f"{title}\n\n{message}"
        if data:
            full_message += "\n\nAdditional Data:\n"
            full_message += "\n".join(f"- {k}: {v}" for k, v in data.items())
        
        results = {
            "email_sent": False,
            "telegram_sent": False,
            "webhook_sent": False,
            "errors": []
        }
        
        # Send email if enabled
        if self.config.email_enabled and self.config.email_recipients:
            try:
                self._send_email(
                    subject=title,
                    message=full_message,
                    recipients=self.config.email_recipients
                )
                results["email_sent"] = True
                logger.info(f"Email notification sent to {len(self.config.email_recipients)} recipients")
            except Exception as e:
                error_msg = f"Failed to send email: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Send Telegram message if enabled
        if self.config.telegram_enabled and self.config.telegram_bot_token and self.config.telegram_chat_id:
            try:
                self._send_telegram(
                    message=full_message,
                    chat_id=self.config.telegram_chat_id
                )
                results["telegram_sent"] = True
                logger.info("Telegram notification sent")
            except Exception as e:
                error_msg = f"Failed to send Telegram message: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Send webhook if enabled
        if self.config.webhook_enabled and self.config.webhook_url:
            try:
                self._send_webhook(
                    payload={
                        "title": title,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": data
                    },
                    url=self.config.webhook_url
                )
                results["webhook_sent"] = True
                logger.info("Webhook notification sent")
            except Exception as e:
                error_msg = f"Failed to send webhook: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        return results
    
    def _send_email(self, subject: str, message: str, recipients: List[str]):
        """Send an email notification"""
        if not self.config.email_sender or not self.config.email_password:
            raise ValueError("Email sender and password must be configured")
        
        msg = MIMEMultipart()
        msg['From'] = self.config.email_sender
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"[Apon AI] {subject}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
            server.starttls()
            server.login(self.config.email_sender, self.config.email_password)
            server.send_message(msg)
    
    def _send_telegram(self, message: str, chat_id: Optional[str] = None):
        """Send a message via Telegram bot"""
        chat_id = chat_id or self.config.telegram_chat_id
        if not self.config.telegram_bot_token or not chat_id:
            raise ValueError("Telegram bot token and chat ID must be configured")
        
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
    
    def _send_webhook(self, payload: Dict, url: Optional[str] = None):
        """Send data to a webhook URL"""
        url = url or self.config.webhook_url
        if not url:
            raise ValueError("Webhook URL must be configured")
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AponAI-NotificationService/1.0"
        }
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()

# Example usage
if __name__ == "__main__":
    # Example configuration (in production, use environment variables)
    config = NotificationConfig(
        email_enabled=True,
        email_sender="your-email@gmail.com",
        email_password="your-app-specific-password",
        email_recipients=["recipient@example.com"],
        
        telegram_enabled=True,
        telegram_bot_token="your-telegram-bot-token",
        telegram_chat_id="your-chat-id",
        
        webhook_enabled=False,
        webhook_url="https://your-webhook-url.com/notifications"
    )
    
    # Initialize notification service
    notifier = NotificationService(config)
    
    # Example notification
    notifier.send_notification(
        title="Price Alert: Milk",
        message="The price of Milk has changed from $2.99 to $3.49 (16.7% increase)",
        data={
            "product_id": "milk-123",
            "old_price": 2.99,
            "new_price": 3.49,
            "change_percent": 16.7,
            "product_url": "https://example.com/products/milk"
        }
    )
