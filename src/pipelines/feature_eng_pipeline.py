import pandas as pd
import yaml
import numpy as np
from pathlib import Path
from datetime import datetime

# Define Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
# CRITICAL UPDATE: We now pull from the Enriched folder, not Preprocessed
ENRICHED_DIR = PROJECT_ROOT / "data" / "02-enriched"
FEATURES_DIR = PROJECT_ROOT / "data" / "03-features"
CONFIG_PATH = PROJECT_ROOT / "config" / "market_data.yaml"

def load_market_config():
    """Loads the vacancy rates and labor indices."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_latest_enriched_file():
    """Finds the most recent CSV in the 02-enriched folder."""
    files = list(ENRICHED_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No enriched data found! Run enrichment_pipeline.py first.")
    return max(files, key=lambda f: f.stat().st_mtime)

def calculate_maintenance_risk(row, market_data):
    """
    Formula: Age * SqFt * Labor_Index
    Logic: Older + Bigger + Scarce Labor = Higher Risk Score
    """
    # 1. Calculate Age
    current_year = datetime.now().year
    # Handle missing yearBuilt by assuming 1980 (avg age)
    year_built = row['yearBuilt'] if pd.notnull(row['yearBuilt']) else 1980
    age = current_year - year_built
    
    # 2. Get Labor Index for this Zip
    zip_code = str(row['zipCode'])
    # Fallback to default if zip not in config
    market_info = market_data['markets'].get(zip_code, market_data['markets']['default'])
    labor_index = market_info['labor_cost_index']
    
    # 3. The Math
    # We divide by 1000 to keep the score readable (e.g., 50 instead of 50,000)
    # Example: 100 yr old house * 2000 sqft * 1.2 index / 1000 = 240 Risk Score
    risk_score = (age * row['squareFootage'] * labor_index) / 1000
    return risk_score

def calculate_vacancy_adjusted_revenue(row, market_data):
    """
    Formula: Gross_Rent * (1 - Vacancy_Rate)
    """
    zip_code = str(row['zipCode'])
    market_info = market_data['markets'].get(zip_code, market_data['markets']['default'])
    vacancy_rate = market_info['vacancy_rate']
    
    gross_rent = row['rent_estimate']
    
    # Safety check
    if pd.isna(gross_rent) or gross_rent == 0:
        return 0
        
    return gross_rent * (1 - vacancy_rate)

def run_feature_engineering():
    print("🚀 Starting Feature Engineering Pipeline...")
    
    # Ensure output folder exists
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Data & Config
    file_path = get_latest_enriched_file()
    print(f"📂 Loading: {file_path.name}")
    df = pd.read_csv(file_path)
    
    market_config = load_market_config()
    
    # 2. Apply "Rent to Cost Ratio" (The 1% Rule)
    # Avoid division by zero
    df['rent_to_cost_ratio'] = df.apply(
        lambda x: (x['rent_estimate'] / x['price']) if x['price'] > 0 else 0, axis=1
    )
    
    # 3. Apply "Maintenance Risk Score"
    df['maintenance_risk_score'] = df.apply(
        lambda row: calculate_maintenance_risk(row, market_config), axis=1
    )
    
    # 4. Apply "Vacancy Adjusted Revenue"
    df['vacancy_adjusted_revenue'] = df.apply(
        lambda row: calculate_vacancy_adjusted_revenue(row, market_config), axis=1
    )
    
    # 5. Save Enriched Data
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"features_kokomo_{timestamp}.csv"
    save_path = FEATURES_DIR / filename
    
    df.to_csv(save_path, index=False)
    
    print(f"✅ Success! Calculated metrics saved to:")
    print(f"   {save_path}")
    
    # Preview the "Secret Sauce" columns
    # We round the columns for cleaner display
    display_cols = ['addressLine1', 'price', 'rent_estimate', 'rent_to_cost_ratio', 'maintenance_risk_score']
    
    print("\n📊 Investor Metrics Preview:")
    print(df[display_cols].round(4).head())

if __name__ == "__main__":
    run_feature_engineering()