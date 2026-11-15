#!/usr/bin/env bash
set -euo pipefail
if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo" >&2
  exit 1
fi
python3 - <<'BACKUP'
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
source = Path('/var/lib/youlian/contacts.sqlite3')
if not source.is_file():
    raise SystemExit('No database to back up')
destination = source.parent / 'backups' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.sqlite3')
with sqlite3.connect(source) as src, sqlite3.connect(destination) as dst:
    src.backup(dst)
print(destination)
BACKUP
