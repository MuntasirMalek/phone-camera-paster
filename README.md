# 📸 Phone Camera Paster

> Snap a photo on your phone → Ctrl+V on your computer.  
> ⚡ Lightning fast · 🔒 100% private via your own WiFi · ☁️ No cloud

![macOS](https://img.shields.io/badge/macOS-supported-blue) ![Windows](https://img.shields.io/badge/Windows-supported-blue) ![Linux](https://img.shields.io/badge/Linux-supported-blue) ![Python](https://img.shields.io/badge/Python-3.6+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

- 📱 **Simple**: Just take a photo on your phone
- ⚡ **Instant**: Photo appears in your clipboard immediately  
- 🔒 **Private**: Everything stays on your local network
- 💻 **Cross-platform**: Works on Mac, Windows, and Linux

---

## 🚀 Quick Start

### 1. Download

```bash
git clone https://github.com/MuntasirMalek/phone-camera-paster.git
cd phone-camera-paster
```

Or [Download ZIP](https://github.com/MuntasirMalek/phone-camera-paster/archive/refs/heads/main.zip) and extract it.

### 2. Install & Start (runs in background)

**Mac:**
```bash
./install-service.sh
```
This installs it as a background service that auto-starts on login!

**Windows:**
```bash
install-service.bat
```
Or double-click `install-service.bat` (run as Administrator)

**Linux:**
```bash
./install-service.sh
```
Requires `xclip` (auto-installed if missing)

All platforms: Installs as a background service that auto-starts on login!

You'll see a URL like:
```
🌐 Server running at: http://192.168.X.X:8765
```

### 3. Open on Your Phone

1. Open your phone's browser
2. Go to the URL shown (e.g., `http://192.168.1.100:8765`)
3. Bookmark it for quick access!

### 4. Take a Photo & Paste!

1. Tap the **shutter button** (big circle)
2. Snap your photo
3. **Ctrl+V** (Windows/Linux) or **Cmd+V** (Mac) to paste anywhere!

### 5. Stop / Uninstall

**Mac (background service):**
```bash
launchctl unload ~/Library/LaunchAgents/com.phonecamerapaster.plist
```

**Windows (background service):**
Delete `PhoneCameraPaster.vbs` from your Startup folder:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```
Then restart or use Task Manager to end the Python process.

**Linux (systemd):**
```bash
systemctl --user stop phonecamerapaster
systemctl --user disable phonecamerapaster
```

---

## 📱 Pro Tips

### Add to Home Screen
For quick access, add the page to your phone's home screen:
- **Chrome**: Menu (⋮) → Add to Home screen
- **Samsung Internet**: Menu → Add page to → Home screen

---

## 🔧 Requirements

| Platform | Requirements |
|----------|-------------|
| **Mac** | Python 3.6+ (pre-installed) |
| **Windows** | Python 3.6+ ([download](https://python.org)) |
| **Linux** | Python 3.6+ (xclip auto-installed by script) |
| **Phone** | Any Android with a browser |
| **Network** | Same Wi-Fi for all devices |

---

## 🛡️ Privacy

- ✅ **100% Local** - No internet required after setup
- ✅ **No Cloud** - Images never leave your network
- ✅ **No Account** - No sign-up, no tracking
- ✅ **Open Source** - See exactly what it does

---

## 🐛 Troubleshooting

**Can't connect from phone?**
- Ensure both devices are on the same Wi-Fi
- Check firewall settings (allow Python/port 8765)

**Camera button opens gallery?**
- Some browsers don't support direct camera access
- Use "or choose from gallery" link, or try Chrome browser

**Windows clipboard not working?**
- Make sure PowerShell is available
- Run as administrator if needed

**"Address already in use" error?**
- The server is already running in another terminal
- Find and close that terminal, or run: `lsof -i :8765` then `kill <PID>`

---

## 📄 License

MIT License - Use it however you like!

---

Made with ❤️ for productivity
