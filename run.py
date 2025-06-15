import os
import subprocess
import sys
import webbrowser
import signal
import time
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.absolute()))

# Import our modules
from scrapers.config_manager import ConfigManager, config
from scrapers.monitor_agent import MonitorAgent
from scrapers.notification_service import NotificationService, NotificationConfig

def print_banner():
    """Print the application banner"""
    banner = """
    █████╗ ██████╗  ██████╗ ███╗   ██╗    ██████╗ ██████╗ ██╗ ██████╗███████╗
   ██╔══██╗██╔══██╗██╔═══██╗████╗  ██║    ██╔══██╗██╔══██╗██║██╔════╝██╔════╝
   ███████║██████╔╝██║   ██║██╔██╗ ██║    ██████╔╝██████╔╝██║██║     █████╗  
   ██╔══██║██╔═══╝ ██║   ██║██║╚██╗██║    ██╔═══╝ ██╔══██╗██║██║     ██╔══╝  
   ██║  ██║██║     ╚██████╔╝██║ ╚████║    ██║     ██║  ██║██║╚██████╗███████╗
   ╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝ ╚═════╝╚══════╝
   
   Grocery Price Monitoring System - Powered by Open Source AI
   ===========================================================
   """
    print(banner)

class AponAI:
    """Main application class for Apon AI"""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize the application with configuration"""
        self.config = config_manager
        self.processes = {}
        self.monitor_agent = None
        self.notification_service = None
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize application services"""
        # Initialize notification service
        notification_config = NotificationConfig(
            email_enabled=self.config.notification.email_enabled,
            email_sender=self.config.notification.email_sender,
            email_password=self.config.notification.email_password,
            email_recipients=self.config.notification.email_recipients,
            smtp_server=self.config.notification.smtp_server,
            smtp_port=self.config.notification.smtp_port,
            telegram_enabled=self.config.notification.telegram_enabled,
            telegram_bot_token=self.config.notification.telegram_bot_token,
            telegram_chat_id=self.config.notification.telegram_chat_id,
            webhook_enabled=self.config.notification.webhook_enabled,
            webhook_url=self.config.notification.webhook_url
        )
        self.notification_service = NotificationService(notification_config)
        
        # Initialize monitor agent
        self.monitor_agent = MonitorAgent(
            data_dir=str(Path(self.config.storage.data_dir) / "monitoring")
        )
    
    def start_monitoring(self):
        """Start the price monitoring service"""
        if not self.config.monitoring.enabled:
            logger.info("Monitoring is disabled in configuration")
            return
        
        logger.info(f"Starting monitoring for {len(self.config.monitoring.urls_to_monitor)} URLs")
        
        # Start monitoring in a separate process
        try:
            self.monitor_agent.schedule_monitoring(
                urls=self.config.monitoring.urls_to_monitor,
                interval_minutes=self.config.monitoring.check_interval_minutes
            )
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring: {e}")
    
    def start_backend(self):
        """Start the Flask backend API"""
        from scrapers.api import app as flask_app
        import threading
        
        def run_flask():
            flask_app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                use_reloader=False
            )
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Backend API started on http://localhost:5000")
        return flask_thread
    
    def start_frontend(self):
        """Start the Next.js frontend"""
        frontend_dir = Path("apps/web")
        if not frontend_dir.exists():
            logger.error(f"Frontend directory not found at {frontend_dir}")
            return None
        
        try:
            # Set environment variables for the frontend
            env = os.environ.copy()
            env["NEXT_PUBLIC_API_URL"] = "http://localhost:5000"
            
            self.processes["frontend"] = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("Frontend started on http://localhost:3000")
            return self.processes["frontend"]
            
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return None
    
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("Installing Python dependencies...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("Python dependencies installed successfully")
            
            # Install Node.js dependencies
            logger.info("Installing Node.js dependencies...")
            subprocess.run(
                ["npm", "install"],
                cwd="apps/web",
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info("Node.js dependencies installed successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error installing dependencies: {e}")
            if e.stderr:
                logger.error(f"Error details: {e.stderr.decode()}")
            return False
    
    def check_environment(self):
        """Check if required tools are installed"""
        required = ["python", "pip", "node", "npm"]
        missing = []
        
        for tool in required:
            try:
                if platform.system() == "Windows":
                    subprocess.run(
                        f"{tool} --version",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                else:
                    subprocess.run(
                        f"which {tool}",
                        shell=True,
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            except subprocess.CalledProcessError:
                missing.append(tool)
        
        return missing
    
    def run(self):
        """Run the application"""
        try:
            # Start backend
            self.start_backend()
            
            # Start frontend
            frontend = self.start_frontend()
            if not frontend:
                logger.warning("Failed to start frontend")
            
            # Start monitoring if enabled
            if self.config.monitoring.enabled:
                self.start_monitoring()
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
        
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shut down the application"""
        logger.info("Shutting down services...")
        
        # Terminate all child processes
        for name, process in self.processes.items():
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)])
                else:
                    process.terminate()
        
        logger.info("Shutdown complete")

def main():
    """Main entry point for the application"""
    try:
        # Print banner
        print_banner()
        
        # Initialize configuration
        config_manager = ConfigManager()
        
        # Check environment
        missing_tools = AponAI(config_manager).check_environment()
        if missing_tools:
            print("\nError: The following required tools are missing:")
            for tool in missing_tools:
                print(f"- {tool}")
            print("\nPlease install them and try again.")
            return 1
        
        # Initialize application
        app = AponAI(config_manager)
        
        # Install dependencies if needed
        if not app.install_dependencies():
            print("\nFailed to install dependencies. Please check the logs for details.")
            return 1
        
        # Run the application
        print("\nStarting Apon AI...")
        print("Press Ctrl+C to stop\n")
        
        app.run()
        return 0
        
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        return 0
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if hasattr(e, '__traceback__'):
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
