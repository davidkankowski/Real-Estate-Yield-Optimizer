import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Define Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PREDICTIONS_DIR = PROJECT_ROOT / "data" / "04-predictions"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures" # Standard place for images

def get_latest_prediction_file():
    files = list(PREDICTIONS_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError("No predictions found. Run scoring_pipeline.py first.")
    return max(files, key=lambda f: f.stat().st_mtime)

def create_yield_risk_matrix(df, save_path):
    """Generates the Quadrant Chart and saves it."""
    
    # Setup the plot
    sns.set_theme(style="white")
    plt.figure(figsize=(12, 8))
    
    # Thresholds (Business Logic)
    RISK_THRESHOLD = 100
    YIELD_THRESHOLD = 0.012

    # Plot Points
    sns.scatterplot(
        data=df,
        x="maintenance_risk_score",
        y="rent_to_cost_ratio",
        hue="deal_score",
        palette="RdYlGn",
        size="deal_score",
        sizes=(200, 600),
        edgecolor="black",
        alpha=0.9
    )
    
    # Draw Quadrant Lines
    plt.axvline(x=RISK_THRESHOLD, color='gray', linestyle='--', alpha=0.5)
    plt.axhline(y=YIELD_THRESHOLD, color='gray', linestyle='--', alpha=0.5)
    
    # Labels
    plt.title("Yield-Risk Matrix: Automated Report", fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Maintenance Risk Score (Lower is Safer) →", fontsize=12)
    plt.ylabel("Rent-to-Cost Ratio (Higher is Better) ↑", fontsize=12)
    
    # Save
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close() # Close plot to free memory

def run_visualization():
    print("🚀 Starting Visualization Pipeline...")
    
    # Ensure reports/figures folder exists
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load Data
    latest_file = get_latest_prediction_file()
    print(f"📊 Visualizing data from: {latest_file.name}")
    df = pd.read_csv(latest_file)
    
    # Create Filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = FIGURES_DIR / f"yield_matrix_{timestamp}.png"
    
    # Generate Chart
    create_yield_risk_matrix(df, save_path)
    
    print(f"✅ Success! Chart saved to:")
    print(f"   {save_path}")

if __name__ == "__main__":
    run_visualization()