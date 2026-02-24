#!/bin/bash
set -e

echo "==================================="
echo "Compiling translations..."
echo "==================================="
cd /app && pybabel compile -d src/i18n/translations

echo "==================================="
echo "Starting supervisord..."
echo "==================================="
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
