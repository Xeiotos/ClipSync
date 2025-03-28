from flask import Flask, request, send_file
import pyperclip
import socket
import os
import shutil
import tempfile
import json

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
            elif os.path.isdir(path):
                shutil.rmtree(path)
        
        # Save new files
        for file_data in content:
            file_path = os.path.join(TEMP_DIR, file_data['name'])
            if file_data.get('is_dir', False):
                os.makedirs(file_path, exist_ok=True)
            else:
                with open(file_path, 'wb') as f:
                    f.write(file_data['content'].encode('latin1'))
    
    return {'status': 'success'}

@app.route('/files/<path:filename>')
def get_file(filename):
    return send_file(os.path.join(TEMP_DIR, filename))

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Clipboard server running on http://{local_ip}:5000")
    print("Keep this window open to receive clipboard content")
    app.run(host='0.0.0.0', port=5000) 