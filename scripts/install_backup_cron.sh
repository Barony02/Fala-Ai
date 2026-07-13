#!/usr/bin/env bash
set -euo pipefail

projeto_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$projeto_dir/backups"
linha="0 18 * * * cd \"$projeto_dir\" && mkdir -p backups && bash scripts/backup_local.sh >> backups/backup.log 2>&1"

(crontab -l 2>/dev/null | grep -v 'scripts/backup_local.sh'; echo "$linha") | crontab -

echo "Backup diário agendado para 18:00."
