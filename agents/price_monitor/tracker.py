import requests
import json
from typing import Dict, Any, List, Optional
from .utils import get_logger
import time

logger = get_logger(__name__)

class PriceChangeTracker:
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url

    def _get_last_snapshot(self, site_name: str, product_name: str) -> Optional[Dict[str, Any]]:
        """Fetches the last snapshot for a specific product from the backend."""
        try:
            response = requests.get(f"{self.api_base_url}/api/snapshots/last", params={
                "site_name": site_name,
                "product_name": product_name
            })
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching last snapshot for {product_name} from {site_name}: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response when fetching last snapshot for {product_name} from {site_name}")
            return None

    def detect_and_store_changes(self, site_name: str, current_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        detected_changes: List[Dict[str, Any]] = []

        for current_product_data in current_data_list:
            product_name = current_product_data.get("product_name")
            if not product_name:
                logger.warning(f"Product name missing in current data for {site_name}. Skipping.")
                continue

            last_snapshot = self._get_last_snapshot(site_name, product_name)

            if not last_snapshot:
                logger.info(f"No previous snapshot found for '{product_name}' on {site_name}. Initial data captured.")
                continue

            last_price = last_snapshot.get("price")
            current_price = current_product_data.get("price")

            last_stock = last_snapshot.get("stock_status")
            current_stock = current_product_data.get("stock_status")

            last_delivery = last_snapshot.get("delivery_time")
            current_delivery = current_product_data.get("delivery_time")

            change_description = []

            if last_price is not None and current_price is not None and last_price != current_price:
                price_change = ((current_price - last_price) / last_price) * 100 if last_price != 0 else 0
                change_description.append(f"Price changed from ৳{last_price:.2f} to ৳{current_price:.2f} ({price_change:.2f}%)")

            if last_stock != current_stock:
                change_description.append(f"Stock status changed from '{last_stock}' to '{current_stock}'")

            if last_delivery != current_delivery:
                change_description.append(f"Delivery time changed from '{last_delivery}' to '{current_delivery}'")

            if change_description:
                detected_changes.append({
                    "product": product_name,
                    "site": site_name,
                    "change_description": ", ".join(change_description),
                    "timestamp": current_product_data.get("timestamp", time.time()),
                    "link": current_product_data.get("scraped_url")
                })
        return detected_changes
