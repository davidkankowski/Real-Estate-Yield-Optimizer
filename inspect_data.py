import json
import pandas as pd
from pathlib import Path
import os

# 1. Find the latest Raw JSON file
PROJECT_ROOT = Path(__file__).resolve().parent
RAW_DIR = PROJECT_ROOT / "data" / "01-raw"
files = list(RAW_DIR.glob("*.json"))
latest_file = max(files, key=os.path.getmtime)

print(f"🕵️‍♀️ Inspecting file: {latest_file.name}")

# 2. Load it into a DataFrame
with open(latest_file, 'r') as f:
    data = json.load(f)

df = pd.json_normalize(data)

# 3. Show me the EXACT column names
print("\n📋 ALL COLUMN NAMES:")
print(df.columns.tolist())

# 4. Show me the EXACT values for Property Type
if 'propertyType' in df.columns:
    print("\n🏠 UNIQUE PROPERTY TYPES (Copy-Paste these!):")
    print(df['propertyType'].unique())
else:
    print("\n❌ 'propertyType' column not found. Check the column list above.")

# 5. Show me a sample of the 'rentEstimate' structure (to see if it's a number or dict)
# We check for columns starting with 'rentEstimate'
rent_cols = [c for c in df.columns if 'rent' in c.lower()]
print(f"\n💰 RENT COLUMNS FOUND: {rent_cols}")
if rent_cols:
    print(df[rent_cols].head())