import shutil
import json
from pathlib import Path

# Paths (adjust if your structure changes)
BACKUP_DIR = Path("vault4paper_backups")
ORIGINAL_PROJECT_DIR = Path("Ansible")
CHANGE_LOG_FILE = Path("vault4paper_change_log.json")

def restore_backups():
    print("Restoring YAML files from backup...")
    if not BACKUP_DIR.exists():
        print("No backup directory found. Nothing to restore.")
        return

    for ext in ("*.yml.bak", "*.yaml.bak"):
        for backup_file in BACKUP_DIR.glob(ext):
            original_filename = backup_file.name.replace(".bak", "")
            original_file = ORIGINAL_PROJECT_DIR / original_filename
            original_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(backup_file, original_file)
            print(f"Restored: {original_file}")

if __name__ == '__main__':
    print("Vault4Paper Antidote Activated!")
    restore_backups()
    print("\nRevert complete.")
