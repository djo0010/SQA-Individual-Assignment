import shutil
from pathlib import Path

# Paths
BACKUP_DIR = Path("vault4paper_backups")
ANSIBLE_DIR = Path("Ansible")
PUPPET_DIR = Path("Puppet")

def restore_backups():
    print("Restoring files from backup...")
    if not BACKUP_DIR.exists():
        print("No backup directory found. Nothing to restore.")
        return

    for backup_file in BACKUP_DIR.rglob("*.bak"):
        original_filename = backup_file.name.replace(".bak", "")

        # Determine destination directory based on file type
        if original_filename.endswith((".yml", ".yaml")):
            original_file = ANSIBLE_DIR / original_filename
        elif original_filename.endswith(".pp"):
            original_file = PUPPET_DIR / original_filename
        else:
            print(f"Skipping unknown backup type: {backup_file}")
            continue

        # Ensure parent directory exists and copy
        original_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(backup_file, original_file)
        print(f"Restored: {original_file}")

if __name__ == '__main__':
    print("Vault4Paper Antidote Activated!")
    restore_backups()
    print("\nRevert complete.")
