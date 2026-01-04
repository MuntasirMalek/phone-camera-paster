#!/bin/bash

# Install Phone Camera Paster as a background service (Mac & Linux)
# Run this once: ./install-service.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Detect Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    PYTHON_PATH="/usr/bin/python3"
fi

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - use launchd
    PLIST_PATH="$HOME/Library/LaunchAgents/com.phonecamerapaster.plist"
    
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.phonecamerapaster</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>${SCRIPT_DIR}/server.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/phonecamerapaster.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/phonecamerapaster.log</string>
</dict>
</plist>
EOF

    launchctl load "$PLIST_PATH"
    
    IP=$(ipconfig getifaddr en0 2>/dev/null || echo 'YOUR_IP')
    
    echo ""
    echo "✅ Phone Camera Paster installed as background service!"
    echo ""
    echo "📱 Open http://${IP}:8765 on your phone"
    echo ""
    echo "To uninstall: launchctl unload $PLIST_PATH && rm $PLIST_PATH"
    echo ""

elif [[ "$OSTYPE" == "linux"* ]]; then
    # Linux - use systemd user service
    SERVICE_DIR="$HOME/.config/systemd/user"
    SERVICE_PATH="$SERVICE_DIR/phonecamerapaster.service"
    
    # Create directory if needed
    mkdir -p "$SERVICE_DIR"
    
    # Check for xclip
    if ! command -v xclip &> /dev/null; then
        echo "⚠️  xclip not found. Installing..."
        if command -v apt &> /dev/null; then
            sudo apt install -y xclip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y xclip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm xclip
        else
            echo "Please install xclip manually: sudo apt install xclip"
        fi
    fi
    
    cat > "$SERVICE_PATH" << EOF
[Unit]
Description=Phone Camera Paster
After=network.target

[Service]
Type=simple
ExecStart=${PYTHON_PATH} ${SCRIPT_DIR}/server.py
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF

    # Reload and enable
    systemctl --user daemon-reload
    systemctl --user enable phonecamerapaster
    systemctl --user start phonecamerapaster
    
    IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "✅ Phone Camera Paster installed as background service!"
    echo ""
    echo "📱 Open http://${IP}:8765 on your phone"
    echo ""
    echo "Commands:"
    echo "  Status:    systemctl --user status phonecamerapaster"
    echo "  Stop:      systemctl --user stop phonecamerapaster"
    echo "  Uninstall: systemctl --user disable phonecamerapaster && rm $SERVICE_PATH"
    echo ""

else
    echo "❌ Unsupported OS: $OSTYPE"
    echo "Please run manually: python3 server.py"
    exit 1
fi
