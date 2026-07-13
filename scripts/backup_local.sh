#!/usr/bin/env bash
set -euo pipefail

mkdir -p backups
arquivo="backups/camara_chamados_$(date +%Y%m%d_%H%M%S).sql"

docker exec camara_db sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" camara_chamados' > "$arquivo"

echo "Backup gerado em $arquivo"
