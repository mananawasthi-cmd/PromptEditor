#!/bin/sh
# Railway injects PORT - use it. Default 5000 for local.
PORT="${PORT:-5000}"
echo "Starting gunicorn on 0.0.0.0:${PORT}"
exec gunicorn --bind "0.0.0.0:${PORT}" --workers 1 --threads 2 --timeout 120 run:app
