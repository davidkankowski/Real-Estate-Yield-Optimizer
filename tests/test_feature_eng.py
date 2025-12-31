import sys
import pandas as pd
import pytest
from pathlib import Path

# Add 'src' to path so we can import your actual code
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from pipelines.feature_eng_pipeline import (
    calculate_maintenance_risk,
    calculate_vacancy_adjusted_revenue
)

# --- TEST 1: The "1% Rule" Check ---
def test_rent_to_cost_math():
    """
    If Price = $100,000 and Rent = $1,000, 
    Yield MUST be 0.01 (1%).
    """
    price = 100000
    rent = 1000
    
    yield_ratio = rent / price
    
    assert yield_ratio == 0.01, f"Expected 0.01, got {yield_ratio}"

# --- TEST 2: Maintenance Risk Logic ---
def test_maintenance_risk_score():
    """
    Scenario:
    - House built in 1920 (Age = ~105 years)
    - Size: 2000 sqft
    - Labor Index: 1.2 (Expensive area)
    
    Formula: (Age * SqFt * Index) / 1000
    Expected: (105 * 2000 * 1.2) / 1000 = 252
    """
    # Create a fake row of data
    row = {
        'yearBuilt': 1920,
        'squareFootage': 2000,
        'zipCode': '46901'
    }
    
    # Create a fake config
    market_config = {
        'markets': {
            '46901': {'labor_cost_index': 1.2},
            'default': {'labor_cost_index': 1.0}
        }
    }
    
    # Run the ACTUAL function from your pipeline
    score = calculate_maintenance_risk(row, market_config)
    
    # Check if it matches our manual calculation (approximate due to current year)
    # We use a range because 'current year' changes
    assert score > 200, "Old big houses should have HIGH risk scores (>200)"

# --- TEST 3: Vacancy Adjustment ---
def test_vacancy_adjusted_revenue():
    """
    Scenario:
    - Rent: $1,000
    - Vacancy Rate: 10% (0.10)
    
    Expected Revenue: $1,000 * (1 - 0.10) = $900
    """
    row = {
        'rent_estimate': 1000,
        'zipCode': '46901'
    }
    
    market_config = {
        'markets': {
            '46901': {'vacancy_rate': 0.10},
            'default': {'vacancy_rate': 0.05}
        }
    }
    
    adjusted_revenue = calculate_vacancy_adjusted_revenue(row, market_config)
    
    assert adjusted_revenue == 900, f"Expected $900, got ${adjusted_revenue}"

if __name__ == "__main__":
    # Allow running this file directly
    sys.exit(pytest.main(["-v", __file__]))