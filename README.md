# Price Monitor

A FastAPI application for monitoring product prices across websites with email notifications.

## Features

- Monitor individual product prices
- Crawl entire websites for product links
- Email notifications for price changes
- Rate limiting to avoid being blocked
- Beautiful dashboard interface
- Support for multiple currencies

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd price-monitor
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure email settings:
   - Copy `.env.example` to `.env`
   - Fill in your email configuration
   - For Gmail, you'll need to create an App Password

5. Run the application:
```bash
python fastapi_price_monitor.py
```

The application will be available at http://127.0.0.1:8080

## Deployment

### Using Docker

1. Build the Docker image:
```bash
docker build -t price-monitor .
```

2. Run the container:
```bash
docker run -p 8080:8080 --env-file .env price-monitor
```

### Using a VPS

1. Set up a VPS with Ubuntu/Debian
2. Install Python 3.8+ and pip
3. Clone the repository
4. Follow the setup steps above
5. Use systemd to run the application as a service:

Create `/etc/systemd/system/price-monitor.service`:
```ini
[Unit]
Description=Price Monitor Service
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/price-monitor
Environment="PATH=/path/to/price-monitor/venv/bin"
ExecStart=/path/to/price-monitor/venv/bin/python fastapi_price_monitor.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable price-monitor
sudo systemctl start price-monitor
```

## Usage

1. Open the dashboard at http://127.0.0.1:8080
2. Enter a product URL or website URL to monitor
3. The application will start monitoring prices
4. You'll receive email notifications when prices change

## Security Notes

- Never commit your `.env` file
- Use environment variables for sensitive data
- Keep your dependencies updated
- Monitor your application logs for any issues

## Contributing

Feel free to submit issues and enhancement requests! 