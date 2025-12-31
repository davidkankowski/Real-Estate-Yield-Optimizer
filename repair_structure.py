import os
from pathlib import Path

def repair_data_folders():
    # Define the folders that were accidentally created as files
    data_path = Path("data")
    subfolders = ["01-raw", "02-preprocessed", "03-features", "04-predictions"]

    print("🔧 Starting Repair...")

    for sub in subfolders:
        target = data_path / sub
        
        # If it exists as a FILE, delete it
        if target.is_file():
            print(f"   🗑️ Deleting file: {target}")
            os.remove(target)
            
        # Now create it as a FOLDER
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Created folder: {target}")
        else:
            print(f"   👍 {target} is already a folder.")

    print("\n🎉 Repairs Complete! You can run the pipeline now.")

if __name__ == "__main__":
    repair_data_folders()