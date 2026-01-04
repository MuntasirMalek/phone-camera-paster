#!/usr/bin/env python3
"""
Phone Camera Paster
Snap a photo on your phone → Ctrl+V on your computer.
Lightning fast, 100% private via your own WiFi. No cloud.
"""

import http.server
import subprocess
import tempfile
import os
import socket
import platform
from datetime import datetime

PORT = 8765
SYSTEM = platform.system()  # 'Darwin' for Mac, 'Windows' for Windows


def copy_image_to_clipboard(image_path):
    """Copy an image to clipboard. Returns (success, error_message)."""
    try:
        if SYSTEM == 'Darwin':  # macOS
            # Use TIFF format which works for both PNG and JPEG
            applescript = f'''
            set theFile to POSIX file "{image_path}"
            set theImage to read theFile as TIFF picture
            set the clipboard to theImage
            '''
            result = subprocess.run(
                ['osascript', '-e', applescript],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, None
            
            # Fallback: try reading as raw data and use pbcopy via a different method
            # Using NSPasteboard via Python's subprocess
            fallback_script = f'''
            use framework "AppKit"
            set theImage to current application's NSImage's alloc()'s initWithContentsOfFile:"{image_path}"
            set thePasteboard to current application's NSPasteboard's generalPasteboard()
            thePasteboard's clearContents()
            thePasteboard's writeObjects:{{theImage}}
            '''
            result2 = subprocess.run(
                ['osascript', '-e', fallback_script],
                capture_output=True,
                text=True
            )
            if result2.returncode == 0:
                return True, None
            return False, result.stderr
            
        elif SYSTEM == 'Windows':
            # PowerShell command to copy image to clipboard
            ps_script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $image = [System.Drawing.Image]::FromFile("{image_path}")
            [System.Windows.Forms.Clipboard]::SetImage($image)
            '''
            result = subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True, None
            return False, result.stderr
            
        elif SYSTEM == 'Linux':
            # Use xclip for Linux (most common)
            # Try xclip first, then xsel as fallback
            try:
                with open(image_path, 'rb') as f:
                    result = subprocess.run(
                        ['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i'],
                        stdin=f,
                        capture_output=True
                    )
                if result.returncode == 0:
                    return True, None
            except FileNotFoundError:
                pass
            
            # Try xsel as fallback
            try:
                with open(image_path, 'rb') as f:
                    result = subprocess.run(
                        ['xsel', '--clipboard', '--input', '--type', 'image/png'],
                        stdin=f,
                        capture_output=True
                    )
                if result.returncode == 0:
                    return True, None
            except FileNotFoundError:
                pass
            
            return False, "Install xclip: sudo apt install xclip"
            
        else:
            return False, f"Unsupported OS: {SYSTEM}"
            
    except Exception as e:
        return False, str(e)

class ClipboardHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                self.send_error(400, "No image data received")
                return
            
            # Read the image data
            image_data = self.rfile.read(content_length)
            
            # Save to temp file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = os.path.join(tempfile.gettempdir(), f"clipboard_photo_{timestamp}.png")
            
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            # Copy to clipboard (cross-platform)
            success, error = copy_image_to_clipboard(temp_path)
            
            if success:
                print(f"✅ Photo copied to clipboard! ({len(image_data)} bytes)")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Photo copied to clipboard!")
            else:
                print(f"❌ Error: {error}")
                self.send_error(500, f"Clipboard error: {error}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_error(500, str(e))
    
    def do_GET(self):
        """Serve the camera capture page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#fafafa">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>📸</title>
    
    <!-- App Icon (SVG Camera) -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='0' y='0' width='100' height='100' fill='%23fafafa'/%3E%3Ccircle cx='50' cy='50' r='35' fill='%23222'/%3E%3Ccircle cx='50' cy='50' r='15' fill='%23333'/%3E%3Ccircle cx='70' cy='25' r='5' fill='%23555'/%3E%3C/svg%3E">
    <link rel="apple-touch-icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='0' y='0' width='100' height='100' fill='%23ffffff'/%3E%3Ccircle cx='50' cy='50' r='35' fill='%23222222'/%3E%3Ccircle cx='50' cy='50' r='15' fill='%23333333'/%3E%3C/svg%3E">
    
    <!-- Web Manifest for Android Install -->
    <link rel="manifest" href="data:application/manifest+json,%7B%22short_name%22%3A%22CamPaste%22%2C%22name%22%3A%22Phone%20Camera%20Paster%22%2C%22icons%22%3A%5B%7B%22src%22%3A%22data%3Aimage%2Fsvg%2Bxml%2C%253Csvg%20xmlns%3D'http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg'%20viewBox%3D'0%200%20100%20100'%253E%253Crect%20x%3D'0'%20y%3D'0'%20width%3D'100'%20height%3D'100'%20fill%3D'%2523ffffff'%2F%253E%253Ccircle%20cx%3D'50'%20cy%3D'50'%20r%3D'35'%20fill%3D'%2523222222'%2F%253E%253C%2Fsvg%253E%22%2C%22type%22%3A%22image%2Fsvg%2Bxml%22%2C%22sizes%22%3A%22any%22%7D%5D%2C%22start_url%22%3A%22.%22%2C%22display%22%3A%22standalone%22%2C%22theme_color%22%3A%22%23fafafa%22%2C%22background_color%22%3A%22%23fafafa%22%7D">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        html, body {
            height: 100%;
            font-family: system-ui, sans-serif;
            background: #fafafa;
            overflow: hidden;
            touch-action: manipulation;
        }
        
        .app {
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            padding: 30px 24px 20px 24px;
        }
        
        /* Top section */
        .top {
            text-align: center;
        }
        
        .title {
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 3px;
            text-transform: uppercase;
            color: #222;
        }
        
        /* Preview area */
        .preview-area {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 35vh;
            flex-shrink: 0;
            margin-top: 30px;
        }
        
        #preview {
            max-width: 65%;
            max-height: 35vh;
            border-radius: 8px;
            display: none;
            box-shadow: 0 10px 40px rgba(0,0,0,0.12);
            object-fit: contain;
        }
        
        .placeholder {
            color: #ccc;
            font-size: 13px;
            letter-spacing: 1px;
        }
        
        /* Status */
        #status {
            height: 24px;
            font-size: 13px;
            color: #888;
            margin-bottom: 20px;
        }
        
        #status.success { color: #22c55e; }
        #status.error { color: #ef4444; }
        
        /* Shutter button */
        .shutter-wrap {
            position: relative;
            width: 80px;
            height: 80px;
        }
        
        .shutter {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 4px solid #222;
            background: white;
            cursor: pointer;
            position: relative;
            transition: transform 0.1s;
        }
        
        .shutter::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: #222;
            transition: all 0.15s;
        }
        
        .shutter:active {
            transform: scale(0.92);
        }
        
        .shutter:active::after {
            width: 48px;
            height: 48px;
            background: #444;
        }
        
        .shutter.flash::after {
            background: #22c55e;
        }
        
        /* Gallery link */
        .gallery-link {
            margin-top: 24px;
            font-size: 13px;
            color: #888;
            text-decoration: underline;
            cursor: pointer;
            background: none;
            border: none;
            font-family: inherit;
        }
        
        /* Bottom hint */
        .hint {
            margin-top: 40px;
            font-size: 11px;
            color: #bbb;
            letter-spacing: 0.5px;
            text-align: center;
            line-height: 1.8;
        }
        
        input[type="file"] { display: none; }
        
        /* Controls (rotate/send) */
        .controls {
            display: flex;
            gap: 12px;
            margin: 15px 0 20px 0;
        }
        
        .rotate-btn, .send-btn {
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.15s;
        }
        
        .rotate-btn {
            background: #f0f0f0;
            border: 1px solid #ddd;
            color: #333;
        }
        
        .rotate-btn:active {
            background: #e0e0e0;
        }
        
        .send-btn {
            background: #222;
            border: none;
            color: white;
        }
        
        .send-btn:active {
            background: #444;
        }
        
        #preview {
            transition: transform 0.2s ease;
        }
        
        /* Loading animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #status.loading {
            animation: pulse 1s ease-in-out infinite;
        }
        
        /* Crop overlay */
        #cropOverlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.95);
            z-index: 1000;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .crop-container {
            position: relative;
            max-width: 90%;
            max-height: 60vh;
        }
        
        #cropImage {
            max-width: 100%;
            max-height: 60vh;
            display: block;
        }
        
        .crop-box {
            position: absolute;
            border: 2px solid #fff;
            box-shadow: 0 0 0 9999px rgba(0,0,0,0.5);
            cursor: move;
            touch-action: none;
        }
        
        .resize-handle {
            position: absolute;
            bottom: -8px;
            right: -8px;
            width: 24px;
            height: 24px;
            background: #fff;
            border-radius: 50%;
            cursor: nwse-resize;
            touch-action: none;
        }
        
        .crop-actions {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="top">
            <div class="title">Photo → Clipboard</div>
        </div>
        
        <div class="preview-area">
            <img id="preview">
            <span class="placeholder" id="placeholder">Your photo will appear here</span>
        </div>
        
        <div class="controls" id="controls" style="display: none;">
            <button class="rotate-btn" id="rotateBtn">↻</button>
            <button class="rotate-btn" id="cropBtn">✂ Crop</button>
            <button class="send-btn" id="sendBtn">Send</button>
        </div>
        
        <!-- Crop overlay -->
        <div id="cropOverlay" style="display: none;">
            <div class="crop-container" id="cropContainer">
                <img id="cropImage">
                <div class="crop-box" id="cropBox">
                    <div class="resize-handle" id="resizeHandle"></div>
                </div>
            </div>
            <div class="crop-actions">
                <button class="rotate-btn" id="cropCancel">Cancel</button>
                <button class="send-btn" id="cropApply">Apply Crop</button>
            </div>
        </div>
        
        <div id="status"></div>
        
        <input type="file" id="camera" accept="image/*" capture>
        <input type="file" id="gallery" accept="image/*">
        
        <div class="shutter-wrap">
            <button class="shutter" id="shutterBtn" aria-label="Take photo"></button>
        </div>
        
        <button class="gallery-link" id="galleryBtn">or choose from gallery</button>
        
        <div class="hint">
            To paste on your computer:<br>
            <span><strong>Ctrl+V</strong> (Windows/Linux)</span><br>
            <span><strong>Cmd+V</strong> (Mac)</span>
        </div>
    </div>
    
    <script>
        const camera = document.getElementById('camera');
        const gallery = document.getElementById('gallery');
        const preview = document.getElementById('preview');
        const placeholder = document.getElementById('placeholder');
        const status = document.getElementById('status');
        const shutterBtn = document.getElementById('shutterBtn');
        const galleryBtn = document.getElementById('galleryBtn');
        const controls = document.getElementById('controls');
        const rotateBtn = document.getElementById('rotateBtn');
        const cropBtn = document.getElementById('cropBtn');
        const sendBtn = document.getElementById('sendBtn');
        
        // Crop elements
        const cropOverlay = document.getElementById('cropOverlay');
        const cropImage = document.getElementById('cropImage');
        const cropBox = document.getElementById('cropBox');
        const cropCancel = document.getElementById('cropCancel');
        const cropApply = document.getElementById('cropApply');
        
        let currentFile = null;
        let rotation = 0;
        let previewUrl = null;
        let cropData = null;
        
        shutterBtn.onclick = () => camera.click();
        galleryBtn.onclick = () => gallery.click();
        
        function cleanup() {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
                previewUrl = null;
            }
        }
        
        function resetUI() {
            cleanup();
            currentFile = null;
            rotation = 0;
            preview.style.display = 'none';
            preview.style.transform = 'rotate(0deg)';
            preview.src = '';
            placeholder.style.display = 'block';
            controls.style.display = 'none';
        }
        
        function loadImage(file) {
            if (!file) return;
            
            cleanup();
            currentFile = file;
            rotation = 0;
            
            previewUrl = URL.createObjectURL(file);
            preview.src = previewUrl;
            preview.style.display = 'block';
            preview.style.transform = 'rotate(0deg)';
            placeholder.style.display = 'none';
            controls.style.display = 'flex';
            status.textContent = '';
            status.className = '';
        }
        
        rotateBtn.onclick = () => {
            rotation = (rotation + 90) % 360;
            preview.style.transform = `rotate(${rotation}deg)`;
        };
        
        // Crop functionality
        cropBtn.onclick = () => {
            if (!currentFile) return;
            cropImage.src = previewUrl;
            cropOverlay.style.display = 'flex';
            
            // Wait for image to load then set initial crop box
            cropImage.onload = () => {
                const rect = cropImage.getBoundingClientRect();
                const size = Math.min(rect.width, rect.height) * 0.8;
                cropBox.style.width = size + 'px';
                cropBox.style.height = size + 'px';
                cropBox.style.left = ((rect.width - size) / 2) + 'px';
                cropBox.style.top = ((rect.height - size) / 2) + 'px';
            };
        };
        
        cropCancel.onclick = () => {
            cropOverlay.style.display = 'none';
        };
        
        cropApply.onclick = async () => {
            const imgRect = cropImage.getBoundingClientRect();
            const boxRect = cropBox.getBoundingClientRect();
            
            // Calculate crop ratios relative to displayed image
            const scaleX = cropImage.naturalWidth / imgRect.width;
            const scaleY = cropImage.naturalHeight / imgRect.height;
            
            cropData = {
                x: (boxRect.left - imgRect.left) * scaleX,
                y: (boxRect.top - imgRect.top) * scaleY,
                width: boxRect.width * scaleX,
                height: boxRect.height * scaleY
            };
            
            // Apply crop to current file
            currentFile = await cropImage2(currentFile, cropData);
            
            // Update preview
            cleanup();
            previewUrl = URL.createObjectURL(currentFile);
            preview.src = previewUrl;
            preview.style.transform = 'rotate(0deg)';
            rotation = 0;
            
            cropOverlay.style.display = 'none';
        };
        
        // Make crop box draggable and resizable
        let isDragging = false;
        let isResizing = false;
        let startX, startY, startLeft, startTop, startW, startH;
        
        const resizeHandle = document.getElementById('resizeHandle');
        
        // Resize handle
        resizeHandle.addEventListener('touchstart', (e) => {
            isResizing = true;
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startW = cropBox.offsetWidth;
            startH = cropBox.offsetHeight;
            e.preventDefault();
            e.stopPropagation();
        });
        
        // Drag crop box
        cropBox.addEventListener('touchstart', (e) => {
            if (isResizing) return;
            isDragging = true;
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startLeft = cropBox.offsetLeft;
            startTop = cropBox.offsetTop;
            e.preventDefault();
        });
        
        document.addEventListener('touchmove', (e) => {
            const touch = e.touches[0];
            const imgRect = cropImage.getBoundingClientRect();
            
            if (isResizing) {
                const dx = touch.clientX - startX;
                const dy = touch.clientY - startY;
                
                let newW = Math.max(50, startW + dx);
                let newH = Math.max(50, startH + dy);
                
                // Constrain to image bounds
                newW = Math.min(newW, imgRect.width - cropBox.offsetLeft);
                newH = Math.min(newH, imgRect.height - cropBox.offsetTop);
                
                cropBox.style.width = newW + 'px';
                cropBox.style.height = newH + 'px';
            } else if (isDragging) {
                const dx = touch.clientX - startX;
                const dy = touch.clientY - startY;
                
                const boxW = cropBox.offsetWidth;
                const boxH = cropBox.offsetHeight;
                
                let newLeft = Math.max(0, Math.min(imgRect.width - boxW, startLeft + dx));
                let newTop = Math.max(0, Math.min(imgRect.height - boxH, startTop + dy));
                
                cropBox.style.left = newLeft + 'px';
                cropBox.style.top = newTop + 'px';
            }
        });
        
        document.addEventListener('touchend', () => {
            isDragging = false;
            isResizing = false;
        });
        
        async function cropImage2(file, crop) {
            return new Promise((resolve) => {
                const img = new Image();
                const url = URL.createObjectURL(file);
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = crop.width;
                    canvas.height = crop.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, crop.x, crop.y, crop.width, crop.height, 0, 0, crop.width, crop.height);
                    canvas.toBlob((blob) => {
                        URL.revokeObjectURL(url);
                        resolve(blob);
                    }, 'image/png');
                };
                img.src = url;
            });
        }
        
        sendBtn.onclick = async () => {
            if (!currentFile) return;
            
            sendBtn.disabled = true;
            status.textContent = 'Sending...';
            status.className = 'loading';
            
            try {
                let blob = currentFile;
                
                if (rotation !== 0) {
                    blob = await rotateImage(currentFile, rotation);
                }
                
                const res = await fetch(location.href, {
                    method: 'POST',
                    body: blob,
                    headers: { 'Content-Type': 'image/png' }
                });
                
                if (res.ok) {
                    status.textContent = '✓ Copied!';
                    status.className = 'success';
                    shutterBtn.classList.add('flash');
                    setTimeout(() => shutterBtn.classList.remove('flash'), 300);
                    if (navigator.vibrate) navigator.vibrate(50);
                    controls.style.display = 'none';
                    currentFile = null;
                } else {
                    status.textContent = 'Failed - tap to retry';
                    status.className = 'error';
                }
            } catch (e) {
                status.textContent = 'No connection';
                status.className = 'error';
            } finally {
                sendBtn.disabled = false;
            }
        };
        
        function rotateImage(file, degrees) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                const url = URL.createObjectURL(file);
                
                img.onload = () => {
                    try {
                        const canvas = document.createElement('canvas');
                        const ctx = canvas.getContext('2d');
                        
                        if (degrees === 90 || degrees === 270) {
                            canvas.width = img.height;
                            canvas.height = img.width;
                        } else {
                            canvas.width = img.width;
                            canvas.height = img.height;
                        }
                        
                        ctx.translate(canvas.width / 2, canvas.height / 2);
                        ctx.rotate(degrees * Math.PI / 180);
                        ctx.drawImage(img, -img.width / 2, -img.height / 2);
                        
                        canvas.toBlob((blob) => {
                            URL.revokeObjectURL(url);
                            resolve(blob);
                        }, 'image/png');
                    } catch (e) {
                        URL.revokeObjectURL(url);
                        reject(e);
                    }
                };
                
                img.onerror = () => {
                    URL.revokeObjectURL(url);
                    reject(new Error('Failed to load image'));
                };
                
                img.src = url;
            });
        }
        
        camera.onchange = (e) => { loadImage(e.target.files[0]); e.target.value = ''; };
        gallery.onchange = (e) => { loadImage(e.target.files[0]); e.target.value = ''; };
    </script>
</body>
</html>'''
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")


def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"


def main():
    local_ip = get_local_ip()
    
    print("\n" + "="*50)
    print("📸 Phone Camera Paster")
    print("="*50)
    print(f"\n🌐 Server running at: http://{local_ip}:{PORT}")
    print(f"\n📱 Open this URL on your phone's browser")
    print("\n" + "="*50)
    print("Waiting for photos...\n")
    
    server = http.server.HTTPServer(('0.0.0.0', PORT), ClipboardHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
