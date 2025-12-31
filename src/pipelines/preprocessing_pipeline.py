import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Define Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "01-raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "02-preprocessed"

def get_latest_raw_file():
    """Finds the most recent JSON file in the 01-raw folder."""
    files = list(RAW_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError("No raw data found! Run extraction_pipeline.py first.")
    
    # Sort files by modification time (newest last) and grab the last one
    latest_file = max(files, key=os.path.getmtime)
    print(f"📂 Processing File: {latest_file.name}")
    return latest_file

def clean_data(df):
    """
    Performs standard cleaning:
    1. Filter for valid property types (No Land/Manufactured)
    2. Ensure numeric types for Price
    3. Prepare empty column for Rent Enrichment
    """
    initial_count = len(df)
    
    # 1. Filter Property Types
    # We only want investment-grade structures:
    valid_types = ['Single Family', 'Multi-Family', 'Condo', 'Townhouse']
    
    if 'propertyType' in df.columns:
        df = df[df['propertyType'].isin(valid_types)]
    
    # 2. Drop rows where 'price' is missing
    df = df.dropna(subset=['price'])
    
    # 3. Handle the Missing Rent Column (The "Placeholder" Strategy)
    # We create this column now so the next pipeline (Enrichment) has a target to fill.
    if 'rentEstimate.price' in df.columns:
        df = df.rename(columns={'rentEstimate.price': 'rent_estimate'})
    else:
        # Create empty column filled with NaN (Not a Number)
        # This prevents the "KeyError" later
        print("⚠️  Notice: Rent data missing in raw file. Creating placeholder for enrichment.")
        df['rent_estimate'] = np.nan

    # 4. Standardize Numeric Columns
    # 'coerce' turns invalid text (like "Contact Agent") into NaN so it doesn't crash math
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['squareFootage'] = pd.to_numeric(df['squareFootage'], errors='coerce')
    df['yearBuilt'] = pd.to_numeric(df['yearBuilt'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')

    print(f"🧹 Cleaned Data: {initial_count} rows -> {len(df)} rows")
    return df

def run_preprocessing():
    print("🚀 Starting Preprocessing Pipeline...")
    
    # Ensure the output directory exists
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Data
    raw_file = get_latest_raw_file()
    with open(raw_file, 'r') as f:
        data = json.load(f)
    
    # 2. Normalize JSON to DataFrame
    df = pd.json_normalize(data)
    
    # 3. Apply Cleaning
    df_clean = clean_data(df)
    
    # 4. Save to CSV
    # We use a consistent name format so the next script can find it easily
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"clean_listings_{timestamp}.csv"
    save_path = PROCESSED_DIR / filename
    
    df_clean.to_csv(save_path, index=False)
    
    print(f"✅ Success! Saved clean data to:")
    print(f"   {save_path}")
    
    # Preview
    cols_to_show = ['addressLine1', 'price', 'propertyType', 'rent_estimate']
    # Only show columns that actually exist
    final_cols = [c for c in cols_to_show if c in df_clean.columns]
    
    print("\n📊 Preview (Ready for Enrichment):")
    print(df_clean[final_cols].head())

if __name__ == "__main__":
    run_preprocessing()