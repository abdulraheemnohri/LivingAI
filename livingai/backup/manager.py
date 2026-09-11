# LivingAI Backup Manager
import os
import shutil
import tarfile
import datetime
import logging
from typing import List, Dict, Any, Optional


class BackupManager:
    """Manages creation, listing, and archiving of backups for database, skills, and configuration."""

    def __init__(self, backup_dir: str, config: Any = None, audit_logger: Any = None):
        self.backup_dir = os.path.expanduser(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)
        self.config = config
        self.audit_logger = audit_logger
        self.livingai_home = os.path.expanduser("~/.livingai")

    def create(self, filename: Optional[str] = None) -> str:
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{timestamp}.tar.gz"

        backup_path = os.path.join(self.backup_dir, filename)

        items_to_backup = [
            ("data", os.path.join(self.livingai_home, "data")),
            ("config", os.path.join(self.livingai_home, "config")),
            ("skills", os.path.join(self.livingai_home, "skills")),
            ("memory", os.path.join(self.livingai_home, "memory")),
        ]

        with tarfile.open(backup_path, "w:gz") as tar:
            for arcname, fullpath in items_to_backup:
                if os.path.exists(fullpath):
                    tar.add(fullpath, arcname=arcname)

        if self.audit_logger:
            self.audit_logger.log("BACKUP_CREATE", f"Created backup {backup_path}")

        print(f"✅ Backup created: {backup_path}")
        return backup_path

    def list(self) -> List[Dict[str, Any]]:
        backups = []
        if not os.path.exists(self.backup_dir):
            return backups

        for f in os.listdir(self.backup_dir):
            if f.endswith(".tar.gz"):
                fp = os.path.join(self.backup_dir, f)
                stat = os.stat(fp)
                backups.append({
                    "filename": f,
                    "path": fp,
                    "size": stat.st_size,
                    "created_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    def restore(self, backup_path: Optional[str] = None) -> bool:
        from .restore import BackupRestore
        restorer = BackupRestore(self.backup_dir, self.audit_logger)
        return restorer.restore(backup_path)
