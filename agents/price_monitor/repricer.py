# agents/price_monitor/repricer.py

import os
import requests
from typing import List, Dict

def reprice_product(product_name: str, competitor_price: float, margin_pct: float) -> float:
    """
    Calculate Apon's new price as (competitor_price - margin_pct%).
    """
    new_price = competitor_price * (1 - (margin_pct / 100.0))
    # Round to two decimal places (currency format)
    return round(new_price, 2)


def push_price_update(api_endpoint: str, api_key: str, product_name: str, new_price: float) -> Dict:
    """
    Calls the store API to update Apon’s product price.
    Returns the JSON response or raises an exception on failure.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "product_name": product_name,
        "new_price": new_price
    }

    response = requests.post(api_endpoint, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def run_repricer(changes: List[Dict], margin_pct: float, api_endpoint: str, api_key: str) -> List[Dict]:
    """
    For each change in the 'changes' list, compute Apon's new price and push the update.
    Returns a list of results, each containing success/failure and details.
    """
    results = []
    for change in changes:
        # Only handle price‐type changes for repricing
        if change.get("change_type") != "price":
            continue

        product = change.get("product")
        old_val = change.get("old_value") # Keep for potential logging, though not used in repricing directly
        new_val = change.get("new_value")

        if product is None or new_val is None: # Basic validation
            results.append({
                "product": product or "Unknown",
                "status": "error",
                "error": "Missing product name or new value for repricing."
            })
            continue
            
        try:
            # Compute Apon's new price
            new_ap_price = reprice_product(product, float(new_val), float(margin_pct))

            resp = push_price_update(api_endpoint, api_key, product, new_ap_price)
            results.append({
                "product": product,
                "repriced_to": new_ap_price,
                "status": "success",
                "response": resp
            })
        except ValueError: # Handle case where new_val or margin_pct might not be convertible to float
             results.append({
                "product": product,
                "status": "error",
                "error": f"Invalid data for repricing: new_value='{new_val}', margin_pct='{margin_pct}'"
            })
        except Exception as e:
            results.append({
                "product": product,
                "repriced_to": new_ap_price if 'new_ap_price' in locals() else "N/A",
                "status": "error",
                "error": str(e)
            })

    return results
