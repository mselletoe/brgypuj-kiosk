from pathlib import Path
from datetime import datetime
import subprocess
import os

# Backup folder
BACKUP_PATH_ENV = os.getenv("KIOSK_BACKUP_DIR", str(Path.home() / "pi_kiosk_backups"))
BACKUP_DIR = Path(BACKUP_PATH_ENV)

# Create the directory if it doesn't exist
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# PostgreSQL connection info
DB_NAME = "kioskdb"
DB_USER = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_PASSWORD = "admin7890"  # For production, use environment variables instead

def create_backup() -> Path:
    """
    Creates a PostgreSQL backup using pg_dump and returns the path to the backup file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = BACKUP_DIR / f"backup_{timestamp}.dump"

    # pg_dump command
    cmd = [
        "pg_dump",
        "-h", DB_HOST,
        "-p", DB_PORT,
        "-U", DB_USER,
        "-F", "c",  # custom format
        "-b",
        "-f", str(backup_file),
        DB_NAME
    ]

    # pg_dump needs password in environment
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    # Run the backup
    subprocess.run(cmd, check=True, env=env)

    if not backup_file.exists():
        raise FileNotFoundError(f"Backup failed: {backup_file} not created")

    print(f"Backup created successfully: {backup_file}")
    return backup_file
