import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ScraperConfig:
    """Configuration for the web scraper"""
    use_proxy: bool = True
    max_retries: int = 3
    request_timeout: int = 10  # seconds
    user_agent_rotation: bool = True
    delay_between_requests: float = 1.0  # seconds
    
    # Proxies (if using)
    proxy_list: List[str] = field(default_factory=lambda: [
        "http://45.79.189.142:80",
        "http://190.64.18.177:80",
        "http://45.79.189.143:80",
        "http://45.79.189.144:80"
    ])

@dataclass
class MonitoringConfig:
    """Configuration for the monitoring service"""
    enabled: bool = True
    check_interval_minutes: int = 60
    price_change_threshold_percent: float = 5.0
    max_products_per_retailer: int = 100
    data_retention_days: int = 30
    timezone: str = "Asia/Dhaka"
    
    # List of URLs to monitor
    urls_to_monitor: List[str] = field(default_factory=lambda: [
        "https://www.walmart.com/cp/food/976759",
        "https://www.target.com/c/grocery/-/N-5xt1a"
    ])

@dataclass
class NotificationConfig:
    """Configuration for notifications"""
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

@dataclass
class LLMConfig:
    """Configuration for language models"""
    model_provider: str = "ollama"  # or "huggingface"
    model_name: str = "mistral"
    temperature: float = 0.1
    max_tokens: int = 1000
    
    # For HuggingFace
    huggingface_api_key: str = ""
    
    # For Ollama
    ollama_base_url: str = "http://localhost:11434"

@dataclass
class StorageConfig:
    """Configuration for data storage"""
    data_dir: str = "data"
    products_file: str = "products.json"
    snapshots_dir: str = "snapshots"
    reports_dir: str = "reports"
    
    def get_products_path(self) -> Path:
        """Get the full path to the products file"""
        return Path(self.data_dir) / self.products_file
    
    def get_snapshots_dir(self) -> Path:
        """Get the full path to the snapshots directory"""
        return Path(self.data_dir) / self.snapshots_dir
    
    def get_reports_dir(self) -> Path:
        """Get the full path to the reports directory"""
        return Path(self.data_dir) / self.reports_dir

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: str = "config.json", env_file: str = ".env"):
        self.config_file = Path(config_file)
        self.env_file = Path(env_file)
        self._load_environment()
        self._load_config()
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"Loaded environment from {self.env_file}")
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                self._from_dict(config_data)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}. Using default configuration.")
                self._set_defaults()
        else:
            logger.info("No config file found. Using default configuration.")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration values"""
        self.scraper = ScraperConfig()
        self.monitoring = MonitoringConfig()
        self.notification = NotificationConfig()
        self.llm = LLMConfig()
        self.storage = StorageConfig()
    
    def _from_dict(self, config_data: Dict[str, Any]):
        """Load configuration from a dictionary"""
        self.scraper = ScraperConfig(**config_data.get("scraper", {}))
        self.monitoring = MonitoringConfig(**config_data.get("monitoring", {}))
        self.notification = NotificationConfig(**config_data.get("notification", {}))
        self.llm = LLMConfig(**config_data.get("llm", {}))
        self.storage = StorageConfig(**config_data.get("storage", {}))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary"""
        return {
            "scraper": asdict(self.scraper),
            "monitoring": asdict(self.monitoring),
            "notification": asdict(self.notification),
            "llm": asdict(self.llm),
            "storage": asdict(self.storage)
        }
    
    def save(self, file_path: Optional[str] = None):
        """Save configuration to a file"""
        save_path = Path(file_path) if file_path else self.config_file
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"Configuration saved to {save_path}")
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        # Update notification settings
        if os.getenv("EMAIL_ENABLED"):
            self.notification.email_enabled = os.getenv("EMAIL_ENABLED").lower() == "true"
        if os.getenv("EMAIL_SENDER"):
            self.notification.email_sender = os.getenv("EMAIL_SENDER")
        if os.getenv("EMAIL_PASSWORD"):
            self.notification.email_password = os.getenv("EMAIL_PASSWORD")
        if os.getenv("EMAIL_RECIPIENTS"):
            self.notification.email_recipients = os.getenv("EMAIL_RECIPIENTS", "").split(",")
        
        # Update LLM settings
        if os.getenv("LLM_MODEL"):
            self.llm.model_name = os.getenv("LLM_MODEL")
        if os.getenv("LLM_PROVIDER"):
            self.llm.model_provider = os.getenv("LLM_PROVIDER")
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.llm.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        logger.info("Configuration updated from environment variables")

# Global configuration instance
config = ConfigManager()

def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config

# Example usage
if __name__ == "__main__":
    # Create a new config manager
    config_manager = ConfigManager()
    
    # Print current configuration
    print("Current configuration:")
    print(json.dumps(config_manager.to_dict(), indent=2))
    
    # Save configuration to file
    config_manager.save("config.example.json")
    print("Example configuration saved to config.example.json")
