# LivingAI Backup Restore
import os
import tarfile
import logging
from typing import Optional, Any


class BackupRestore:
    """Restores database, config, skills, and memory state from a backup archive."""

    def __init__(self, backup_dir: str, audit_logger: Any = None):
        self.backup_dir = os.path.expanduser(backup_dir)
        self.audit_logger = audit_logger
        self.livingai_home = os.path.expanduser("~/.livingai")

    def restore(self, backup_path: Optional[str] = None) -> bool:
        if not backup_path:
            backups = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.endswith(".tar.gz")]
            if not backups:
                print("❌ No backups found to restore.")
                return False
            backups.sort(key=os.path.getmtime, reverse=True)
            backup_path = backups[0]

        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_path}")
            return False

        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(path=self.livingai_home)

            if self.audit_logger:
                self.audit_logger.log("BACKUP_RESTORE", f"Restored backup {backup_path}")

            print(f"✅ Backup restored successfully from {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Backup restore failed: {e}")
            print(f"❌ Backup restore failed: {e}")
            return False
