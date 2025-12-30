import os

def create_structure():
    # 1. Define the 8-Point Structure (Professional Template)
    structure = {
        "config": ["model_params.yaml", "market_data.yaml", "investor_profile.yaml"],
        "data": ["01-raw", "02-preprocessed", "03-features", "04-predictions"],
        "entrypoint": ["ingest.py", "score.py"],
        "notebooks": ["01_Exploratory_Analysis.ipynb", "02_Metric_Definition.ipynb"],
        "src": ["__init__.py", "utils.py"],
        "src/pipelines": ["__init__.py", "extraction_pipeline.py", "feature_eng_pipeline.py", "scoring_pipeline.py"],
        "tests": ["__init__.py", "test_feature_eng.py"],
        "docker": ["Dockerfile", "env.yaml"],
        ".": ["requirements.txt", "README.md", ".gitignore", ".env"] # Root files
    }

    print("🚀 Initializing Real Estate Yield-Risk Engine...")

    # 2. Create Folders and Files
    for folder, files in structure.items():
        # Create the folder
        os.makedirs(folder, exist_ok=True)
        
        for file in files:
            # Handle files that belong in the root (".") vs nested folders
            if folder == ".":
                file_path = file
            else:
                file_path = os.path.join(folder, file)
            
            # Create empty file if it doesn't exist
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    # Write a tiny header so the file isn't 0KB
                    if file.endswith(".yaml"):
                        f.write("# Config file\n")
                    elif file.endswith(".py"):
                        f.write(f"# {file} - Module created automatically\n")
                    elif file.endswith(".md"):
                        f.write(f"# Project Documentation\n")
                    elif file == ".gitignore":
                        # CRITICAL: Add security defaults immediately
                        f.write(".env\n__pycache__/\n*.csv\n.DS_Store\n")
                print(f"✅ Created {file_path}")
            else:
                print(f"⚠️ {file_path} already exists")

    print("\n🎉 New Project Skeleton Created Successfully!")
    print("👉 Next Step: Open '.env' and paste your RentCast API Key.")

if __name__ == "__main__":
    create_structure()