import shutil
import os
from pathlib import Path

def cleanup_repo():
    print("🧹 Starting Repository Cleanup...")
    
    # Define the root directory
    root = Path(__file__).parent.resolve()
    
    # List of items to delete (Files and Folders)
    items_to_remove = [
        root / "docker",                      # Folder
        root / "entrypoint",                  # Folder
        root / "notebooks" / "02_Metric_Definition.ipynb", # File
        root / "src" / "utils.py",            # File
        root / "src" / "__init__.py"          # File
    ]
    
    for item in items_to_remove:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"   🗑️  Deleted Folder: {item.name}")
                else:
                    os.remove(item)
                    print(f"   🗑️  Deleted File:   {item.name}")
            except Exception as e:
                print(f"   ❌ Error deleting {item.name}: {e}")
        else:
            print(f"   ⚠️  Skipped (Not Found): {item.name}")

    print("\n✅ Cleanup Complete! Don't forget to commit these changes to GitHub.")

if __name__ == "__main__":
    cleanup_repo()