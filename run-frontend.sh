#!/bin/bash
# Load nvm and run frontend (use this if npm is not in PATH)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
cd "$(dirname "$0")/frontend" && npm install && npm run dev
