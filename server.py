from flask import Flask, request, send_file
import pyperclip
import socket
import os
import tempfile
import subprocess
import base64

app = Flask(__name__)

# Create a temporary directory for file transfers
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'clipsync')
os.makedirs(TEMP_DIR, exist_ok=True)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def copy_to_clipboard(file_path):
    """Copy file to Windows clipboard using PowerShell"""
    try:
        # Convert path to Windows format
        win_path = file_path.replace('/', '\\')
        # Use PowerShell to copy file to clipboard
        subprocess.run(['powershell', '-Command', f'Set-Clipboard -Path "{win_path}"'], check=True)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False

@app.route('/clipboard', methods=['POST'])
def receive_clipboard():
    data = request.json
    content_type = data.get('type', 'text')
    content = data.get('content', '')
    
    if content_type == 'text':
        pyperclip.copy(content)
    elif content_type == 'files':
        # Clear previous files
        for item in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, item)
            if os.path.isfile(path):
                os.unlink(path)
        
        # Save new file
        if content:
            file_data = content[0]  # Only handle the first file
            file_path = os.path.join(TEMP_DIR, file_data['name'])
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data['content']))
            
            # Copy to clipboard
            copy_to_clipboard(file_path)
    
    return {'status': 'success'}

@app.route('/files/<path:filename>')
def get_file(filename):
    return send_file(os.path.join(TEMP_DIR, filename))

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Clipboard server running on http://{local_ip}:5000")
    print("Keep this window open to receive clipboard content")
    app.run(host='0.0.0.0', port=5000) 