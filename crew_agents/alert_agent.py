from crewai import Agent, Tool
from langchain.tools import BaseTool
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
from i18n import t as translate

load_dotenv()

class TwilioAlertTool(BaseTool):
    name = "twilio_alert"
    description = "Sends SMS alerts using Twilio"

    def __init__(self):
        super().__init__()
        self.client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

    def _run(self, alert_data: str) -> str:
        """Send SMS alert using Twilio"""
        data = json.loads(alert_data)
        
        # Get localized message
        message = translate(
            "alerts.price_change", 
            product=data["product"],
            old_price=data["old_price"],
            new_price=data["new_price"]
        )
        
        try:
            message = self.client.messages.create(
                body=message,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=data["phone_number"]
            )
            return json.dumps({"status": "success", "message_sid": message.sid})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    async def _arun(self, alert_data: str) -> str:
        return self._run(alert_data)

class EmailAlertTool(BaseTool):
    name = "email_alert"
    description = "Sends email alerts using SMTP"

    def _run(self, alert_data: str) -> str:
        """Send email alert"""
        data = json.loads(alert_data)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = os.getenv("SMTP_FROM")
        msg['To'] = data["email"]
        msg['Subject'] = translate("alerts.price_change_subject")
        
        # Add localized body
        body = translate(
            "alerts.price_change_email",
            product=data["product"],
            old_price=data["old_price"],
            new_price=data["new_price"]
        )
        msg.attach(MIMEText(body, 'html'))
        
        try:
            with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT", "587"))) as server:
                server.starttls()
                server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
                server.send_message(msg)
            return json.dumps({"status": "success"})
        except Exception as e:
            return json.dumps({"status": "error", "error": str(e)})

    async def _arun(self, alert_data: str) -> str:
        return self._run(alert_data)

class AlertAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Alert Coordinator",
            goal="Generate and send price change notifications",
            tools=[TwilioAlertTool(), EmailAlertTool()],
            verbose=True
        )

    def generate_alert(self, price_change: Dict[str, Any]) -> Dict[str, Any]:
        """Generate and send alerts for significant price changes"""
        # Check if change exceeds threshold (5%)
        if abs(price_change["change_percentage"]) >= 5:
            # Prepare alert data
            alert_data = {
                "product": price_change["product"],
                "old_price": price_change["old_price"],
                "new_price": price_change["new_price"],
                "phone_number": price_change["phone_number"],
                "email": price_change["email"]
            }
            
            # Send SMS alert
            sms_result = self.execute(json.dumps(alert_data), tool_name="twilio_alert")
            
            # Send email alert
            email_result = self.execute(json.dumps(alert_data), tool_name="email_alert")
            
            return {
                "sms": json.loads(sms_result),
                "email": json.loads(email_result)
            }
        return {"status": "no_alert", "reason": "change_below_threshold"}

if __name__ == "__main__":
    # Example usage
    agent = AlertAgent()
    result = agent.generate_alert({
        "product": "Product A",
        "old_price": 100,
        "new_price": 105,
        "phone_number": "+8801234567890",
        "email": "user@example.com"
    })
    print(result)
