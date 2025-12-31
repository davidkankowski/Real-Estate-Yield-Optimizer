import os
import json
import requests
import yaml
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# 1. Load Environment Variables (Robust Method)
# This finds the 'Real_Estate_Yield_Optimizer' root folder automatically
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("RENTCAST_API_KEY")

def load_config():
    """Loads the zip codes and settings from the YAML config file."""
    # Uses project_root to ensure it finds the file no matter where you run this script from
    config_path = project_root / "config" / "investor_profile.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def fetch_listings(zip_code):
    """
    Connects to RentCast API to get active sale listings for a specific zip.
    """
    url = "https://api.rentcast.io/v1/listings/sale"
    
    # Original Method: Send Key in the Header (Cleaner)
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY
    }
    
    # Parameters for the API call
    params = {
        "zipCode": zip_code,
        "status": "Active",
        "limit": 50  # Get up to 50 houses per zip
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # Check for errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data for {zip_code}: {e}")
        return []

def run_extraction():
    """
    Main orchestration function:
    1. Reads Config
    2. Loops through Zips
    3. Saves Raw Data
    """
    print("🚀 Starting Extraction Pipeline...")
    
    # A. Load Config
    config = load_config()
    target_zips = config["target_market"]["zip_codes"]
    city = config["target_market"]["city"]
    
    all_listings = []
    
    # B. Loop through Zip Codes
    for zip_code in target_zips:
        print(f"   Searching {zip_code}...")
        data = fetch_listings(zip_code)
        
        # Check if we got listings back
        if isinstance(data, list):
            listings = data # Sometimes it returns a list directly
        else:
            listings = data.get("listings", []) # Sometimes it's inside a key
            
        print(f"   Found {len(listings)} listings in {zip_code}")
        all_listings.extend(listings)
    
    # C. Save Raw Data
    # Create a filename with the timestamp so we never overwrite old data
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"raw_listings_{city}_{timestamp}.json"
    
    # Construct the full path to the save location
    save_path = project_root / "data" / "01-raw" / filename
    
    # Save the file
    with open(save_path, "w") as f:
        json.dump(all_listings, f, indent=4)
        
    print(f"\n✅ Success! Saved {len(all_listings)} listings to:")
    print(f"   {save_path}")

if __name__ == "__main__":
    run_extraction()