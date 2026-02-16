#!/bin/bash
# Install backend deps (works around pip SSL certificate issues)

set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

source venv/bin/activate

pip install --trusted-host pypi.org \
            --trusted-host pypi.python.org \
            --trusted-host files.pythonhosted.org \
            -r requirements.txt

echo "Backend dependencies installed. Run: source venv/bin/activate && python run.py"
