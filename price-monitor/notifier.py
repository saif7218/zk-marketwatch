import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Notifier:
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587, sender_email="", sender_password=""):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    async def notify_price_drop(self, product, price, summary):
        if not self.sender_email or not self.sender_password:
            print("Notifier: Email config missing.")
            return
        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = product.user.email
        msg["Subject"] = f"Price Drop: {product.name}"
        body = f"{summary}\nNew price: {price}\nProduct: {product.url}"
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, product.user.email, msg.as_string())

    async def notify_bundle(self, user_id, results, total):
        # Implement as needed (email, SMS, etc.)
        pass

    async def notify_prediction(self, product, prediction):
        # Implement as needed (email, SMS, etc.)
        pass
