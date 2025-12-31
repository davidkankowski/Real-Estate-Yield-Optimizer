import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime

# Define Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_DIR = PROJECT_ROOT / "data" / "03-features"
PREDICTIONS_DIR = PROJECT_ROOT / "data" / "04-predictions"
CONFIG_PATH = PROJECT_ROOT / "config" / "model_params.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_latest_features_file():
    files = list(FEATURES_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No feature data found! Run feature_eng_pipeline.py first.")
    return max(files, key=lambda f: f.stat().st_mtime)

def calculate_score(row, config):
    """
    Calculates a 0-100 score based on weighted priorities.
    """
    weights = config['weights']
    limits = config['scaling']
    
    # 1. Score the Yield (Higher is Better)
    # If Yield is 1.5% (target), score is 1.0. If 0.75%, score is 0.5.
    yield_score = min(row['rent_to_cost_ratio'] / limits['target_yield'], 1.0)
    
    # 2. Score the Maintenance Risk (Lower is Better)
    # We invert it: 0 risk = 1.0 score. Max risk = 0.0 score.
    risk_raw = row['maintenance_risk_score']
    # Ensure we don't go below 0
    risk_score = max(1 - (risk_raw / limits['max_risk_score']), 0.0)
    
    # 3. Score the Vacancy Adjusted Revenue (Higher is Better)
    # We normalize this by Price to keep it comparable (Revenue per dollar spent)
    # This is a secondary yield metric.
    if row['price'] > 0:
        rev_score = min((row['vacancy_adjusted_revenue'] * 12) / row['price'] / limits['target_yield'], 1.0)
    else:
        rev_score = 0
    
    # 4. Weighted Sum
    final_score = (
        (yield_score * weights['rent_to_cost']) +
        (risk_score * weights['maintenance_risk']) +
        (rev_score * weights['vacancy_adjusted'])
    )
    
    # Convert to 0-100 scale
    return round(final_score * 100, 1)

def run_scoring():
    print("🚀 Starting Scoring Pipeline (The Final Ranking)...")
    
    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Data & Config
    file_path = get_latest_features_file()
    print(f"📂 Loading: {file_path.name}")
    df = pd.read_csv(file_path)
    config = load_config()
    
    # 2. Calculate Deal Score
    df['deal_score'] = df.apply(lambda row: calculate_score(row, config), axis=1)
    
    # 3. Sort by Score (Best Deals First)
    df_sorted = df.sort_values(by='deal_score', ascending=False)
    
    # 4. Save Final Report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"final_rankings_{timestamp}.csv"
    save_path = PREDICTIONS_DIR / filename
    
    df_sorted.to_csv(save_path, index=False)
    
    print(f"✅ Success! Top deals saved to:")
    print(f"   {save_path}")
    
    # Preview the Winners
    print("\n🏆 TOP 5 DEALS IN KOKOMO:")
    cols = ['deal_score', 'addressLine1', 'price', 'rent_to_cost_ratio', 'maintenance_risk_score']
    print(df_sorted[cols].head(5))

if __name__ == "__main__":
    run_scoring()