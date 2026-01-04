#!/bin/bash

# Phone Camera Paster - Start Script
# Double-click this file or run: ./start.sh

cd "$(dirname "$0")"

echo ""
echo "📸 Starting Phone Camera Paster..."
echo ""

python3 server.py
