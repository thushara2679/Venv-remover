import os
import time
from datetime import datetime

# 🔧 SETTINGS
ROOT_DIR = "D:/"        # 👈 Change this to where your projects are stored
DAYS_UNUSED = 60         # Delete venvs not modified in last X days
MIN_SIZE_MB = 200        # Only delete if size > X MB (optional safeguard)
DRY_RUN = True           # True = preview only, False = actually delete

def get_folder_size(folder):
    total = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)  # Convert bytes to MB

def cleanup_venvs(root):
    now = time.time()
    deleted = 0
    skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        if "venv" in dirnames:
            venv_path = os.path.join(dirpath, "venv")
            try:
                last_modified = os.path.getmtime(venv_path)
                age_days = (now - last_modified) / (60 * 60 * 24)
                size_mb = get_folder_size(venv_path)

                if age_days > DAYS_UNUSED and size_mb > MIN_SIZE_MB:
                    print(f"\n🗑️ Found old venv: {venv_path}")
                    print(f"   → Last modified: {int(age_days)} days ago")
                    print(f"   → Size: {int(size_mb)} MB")
                    if not DRY_RUN:
                        import shutil
                        shutil.rmtree(venv_path)
                        print("   ✅ Deleted.")
                    else:
                        print("   ⚠️ (Dry run — not deleted)")
                    deleted += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"❌ Error checking {venv_path}: {e}")
    print(f"\n--- Done ---\nDeleted: {deleted} | Skipped: {skipped}")

if __name__ == "__main__":
    print(f"🔍 Scanning {ROOT_DIR} for unused venv folders...")
    cleanup_venvs(ROOT_DIR)
