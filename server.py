from flask import Flask, request, send_file
import pyperclip
import socket
import os
import tempfile
import subprocess
import base64
import shutil

app = Flask(__name__)

# Create a temporary directory for file transfers
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'clipsync')
os.makedirs(TEMP_DIR, exist_ok=True)

def get_local_ip():
    """Get the local IP address for network connections"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Use Google's DNS to determine which interface to use
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        # Fallback to localhost if no network connection
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

def clean_temp_directory():
    """Remove all files from the temporary directory"""
    try:
        for item in os.listdir(TEMP_DIR):
            path = os.path.join(TEMP_DIR, item)
            if os.path.isfile(path):
                os.unlink(path)
        return True
    except Exception as e:
        print(f"Error cleaning temporary directory: {e}")
        return False

@app.route('/clipboard', methods=['POST'])
def receive_clipboard():
    """
    Handle incoming clipboard content from the client
    
    Accepts:
    - Text content: Copies directly to clipboard
    - File content: Saves to temp directory and copies to clipboard
    """
    try:
        data = request.json
        content_type = data.get('type', 'text')
        content = data.get('content', '')
        
        if content_type == 'text':
            if not content:
                return {'status': 'error', 'message': 'Empty text content'}
            
            pyperclip.copy(content)
            return {'status': 'success', 'message': 'Text copied to clipboard'}
            
        elif content_type == 'files':
            # Clear previous files
            clean_temp_directory()
            
            # Make sure we have content to process
            if not content:
                return {'status': 'error', 'message': 'No file content received'}
            
            file_data = content[0]  # Only handle the first file
            if 'name' not in file_data or 'content' not in file_data:
                return {'status': 'error', 'message': 'Invalid file data format'}
                
            # Save file to temp directory
            file_path = os.path.join(TEMP_DIR, file_data['name'])
            with open(file_path, 'wb') as f:
                f.write(base64.b64decode(file_data['content']))
            
            # Copy to clipboard
            if copy_to_clipboard(file_path):
                return {'status': 'success', 'message': f'File copied to clipboard: {file_data["name"]}'}
            else:
                return {'status': 'error', 'message': 'Failed to copy file to clipboard'}
        else:
            return {'status': 'error', 'message': f'Unsupported content type: {content_type}'}
    
    except Exception as e:
        print(f"Error processing clipboard content: {e}")
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/files/<path:filename>')
def get_file(filename):
    """Serve a file from the temporary directory"""
    try:
        file_path = os.path.join(TEMP_DIR, filename)
        if not os.path.exists(file_path):
            return {'status': 'error', 'message': 'File not found'}, 404
        return send_file(file_path)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/health')
def health_check():
    """Simple endpoint to check if server is running"""
    return {'status': 'ok', 'temp_dir': TEMP_DIR}

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Clipboard server running on http://{local_ip}:5000")
    print(f"Temporary files will be stored in: {TEMP_DIR}")
    print("Keep this window open to receive clipboard content")
    app.run(host='0.0.0.0', port=5000) 