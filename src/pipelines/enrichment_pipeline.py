import os
import requests
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 1. Setup Paths & Config
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREPROCESSED_DIR = PROJECT_ROOT / "data" / "02-preprocessed"
ENRICHED_DIR = PROJECT_ROOT / "data" / "02-enriched" # New folder for this step
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path)

API_KEY = os.getenv("RENTCAST_API_KEY")

def get_latest_preprocessed_file():
    files = list(PREPROCESSED_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No clean data found! Run preprocessing_pipeline.py first.")
    return max(files, key=os.path.getmtime)

def fetch_rent_estimate(address, property_type, bedrooms, bathrooms, square_footage):
    """
    Calls the RentCast AVM Endpoint (The 'Sniper' Shot).
    We pass extra details (beds/baths) to make the estimate more accurate.
    """
    url = "https://api.rentcast.io/v1/avm/rent/long-term"
    
    headers = {
        "accept": "application/json",
        "X-Api-Key": API_KEY
    }
    
    params = {
        "address": address,
        "propertyType": property_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "squareFootage": square_footage
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # We only care about the 'rent' value for now
        return data.get("rent", 0)
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API Error for {address[:15]}...: {e}")
        return 0


def run_enrichment():
    print("🚀 Starting Enrichment Pipeline (Safety Mode)...")
    
    # 0. Ensure Output Directory Exists
    ENRICHED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Load Clean Data
    file_path = get_latest_preprocessed_file()
    print(f"📂 Loading: {file_path.name}")
    df = pd.read_csv(file_path)
    
    # --- INTELLIGENT FILTERING ---
    df_sorted = df.sort_values(by='price', ascending=True)
    
    # 2. Loop and Enrich (WITH SAFETY BRAKE)
    rents = []
    enriched_rows = []
    
    # HARD LIMIT: Stop after exactly 5 calls to protect your wallet
    MAX_CALLS = 5 
    call_count = 0
    
    # We loop through the sorted list, but the 'break' below ensures we stop at MAX_CALLS
    for index, row in df_sorted.iterrows():
        
        if call_count >= MAX_CALLS:
            print(f"🛑 SAFETY LIMIT REACHED: Stopped after {MAX_CALLS} API calls.")
            break
            
        print(f"   [{call_count + 1}/{MAX_CALLS}] 🔎 Fetching rent for: {row['addressLine1']} (${row['price']:,.0f})")
        
        estimated_rent = fetch_rent_estimate(
            address=row['formattedAddress'],
            property_type=row['propertyType'],
            bedrooms=row['bedrooms'],
            bathrooms=row['bathrooms'],
            square_footage=row['squareFootage']
        )
        
        # Only increment our counter if we actually made a call
        call_count += 1
        
        if estimated_rent > 0:
            print(f"      ✅ Rent Estimate: ${estimated_rent}")
            # Add to our results list
            row['rent_estimate'] = estimated_rent
            enriched_rows.append(row)
        else:
            print(f"      ⚠️ No rent data found.")
            # Even if we found nothing, we still paid for the API call, so we skip adding it to the final list
            # unless you want to keep it with rent=0
        
        time.sleep(0.5)

    # 3. Create DataFrame from the successful hits
    if enriched_rows:
        final_df = pd.DataFrame(enriched_rows)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"enriched_listings_{timestamp}.csv"
        save_path = ENRICHED_DIR / filename
        
        final_df.to_csv(save_path, index=False)
        
        print(f"\n✅ Enrichment Complete! Saved {len(final_df)} listings to:")
        print(f"   {save_path}")
    else:
        print("\n⚠️ No data was enriched. Check your API key or data source.")

if __name__ == "__main__":
    run_enrichment()
        
