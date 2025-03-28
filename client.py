import pyperclip
import requests
import time
import sys
import os
import base64
from pathlib import Path

def send_clipboard(server_url):
    last_content = ''
    last_files = set()
    
    print(f"Monitoring clipboard. Press Ctrl+C to exit.")
    print(f"Sending to server: {server_url}")
    
    def get_clipboard_files():
        try:
            # On macOS, we can get file paths from the clipboard
            files = pyperclip.paste().split('\n')
            return [f for f in files if os.path.exists(f) and os.path.isfile(f)]  # Only return files, not directories
        except:
            return []

    def read_file_content(file_path):
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def prepare_file_data(file_path):
        """Prepare data for a single file"""
        content = read_file_content(file_path)
        if content is not None:
            return {
                'name': os.path.basename(file_path),
                'content': content
            }
        return None

    try:
        while True:
            # Check for text content
            current_content = pyperclip.paste()
            
            # Check for files
            current_files = set(get_clipboard_files())
            
            if current_content != last_content or current_files != last_files:
                if current_files:
                    # Send files
                    file_data = prepare_file_data(next(iter(current_files)))  # Only send the first file
                    if file_data:
                        try:
                            response = requests.post(
                                f"{server_url}/clipboard",
                                json={'type': 'files', 'content': [file_data]}
                            )
                            if response.status_code == 200:
                                print(f"Sent file: {file_data['name']}")
                        except requests.exceptions.RequestException as e:
                            print(f"Error sending file: {e}")
                elif current_content.strip():
                    # Send text
                    try:
                        response = requests.post(
                            f"{server_url}/clipboard",
                            json={'type': 'text', 'content': current_content}
                        )
                        if response.status_code == 200:
                            print(f"Sent text: {current_content[:50]}...")
                    except requests.exceptions.RequestException as e:
                        print(f"Error sending text: {e}")
                
                last_content = current_content
                last_files = current_files
            
            time.sleep(0.5)  # Check every 500ms
            
    except KeyboardInterrupt:
        print("\nStopping clipboard monitor...")
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python client.py <server_url>")
        print("Example: python client.py http://192.168.1.100:5000")
        sys.exit(1)
    
    server_url = sys.argv[1]
    send_clipboard(server_url) 