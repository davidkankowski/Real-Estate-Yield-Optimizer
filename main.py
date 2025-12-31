import sys
import time
from pathlib import Path

# Add the 'src' folder to the python path so imports work correctly
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from pipelines.extraction_pipeline import run_extraction
from pipelines.preprocessing_pipeline import run_preprocessing
from pipelines.enrichment_pipeline import run_enrichment
from pipelines.feature_eng_pipeline import run_feature_engineering
from pipelines.scoring_pipeline import run_scoring

def print_separator(step_name):
    print("\n" + "="*60)
    print(f"🚦 STEP: {step_name}")
    print("="*60)

def main():
    print("🏗️  STARTING REAL ESTATE YIELD OPTIMIZER PIPELINE")
    start_time = time.time()
    
    try:
        # 1. Extraction (Get Raw Data)
        print_separator("EXTRACTION")
        run_extraction()
        
        # 2. Preprocessing (Clean Data)
        print_separator("PREPROCESSING")
        run_preprocessing()
        
        # 3. Enrichment (Get Rent Estimates)
        print_separator("ENRICHMENT (Top 5 Candidates)")
        run_enrichment()
        
        # 4. Feature Engineering (Calculate Yield & Risk)
        print_separator("FEATURE ENGINEERING")
        run_feature_engineering()
        
        # 5. Scoring (Rank Deals)
        print_separator("SCORING & RANKING")
        run_scoring()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print(f"✅ PIPELINE COMPLETE in {duration:.2f} seconds")
        print("="*60)
        print("Check 'data/04-predictions' for your final report.")

    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()