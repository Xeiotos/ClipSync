import pyperclip
import requests
import time
import sys
import os
import base64
import subprocess
from pathlib import Path

def send_clipboard(server_url):
    last_content = ''
    last_files = set()
    
    print(f"Monitoring clipboard. Press Ctrl+C to exit.")
    print(f"Sending to server: {server_url}")
    
    def get_clipboard_files():
        """
        Check if the clipboard contains files and retrieve their paths.
        Uses a multi-step approach with AppleScript and pbpaste.
        """
        try:
            # First check if clipboard has file references
            check_script = '''
            set cbInfo to (clipboard info) as string
            if cbInfo contains "«class furl»" then
                return "has_files"
            else
                return "no_files"
            end if
            '''
            
            check_result = subprocess.run(['osascript', '-e', check_script], capture_output=True, text=True)
            
            if check_result.stdout.strip() != "has_files":
                return []
            
            # Try to get file path directly from pbpaste
            pbpaste_result = subprocess.run(['pbpaste', '-Prefer', 'txt'], capture_output=True, text=True)
            potential_path = pbpaste_result.stdout.strip()
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                return [potential_path]
            
            # Fallback to AppleScript for file references
            get_paths_script = '''
            try
                tell application "Finder"
                    set theClipboard to the clipboard as «class furl»
                    set filePaths to {}
                    
                    if class of theClipboard is list then
                        repeat with aFile in theClipboard
                            set the end of filePaths to POSIX path of (aFile as string)
                        end repeat
                    else
                        set the end of filePaths to POSIX path of (theClipboard as string)
                    end if
                    
                    return filePaths
                end tell
            on error errMsg
                return "Error: " & errMsg
            end try
            '''
            
            paths_result = subprocess.run(['osascript', '-e', get_paths_script], capture_output=True, text=True)
            
            if paths_result.returncode == 0 and paths_result.stdout.strip():
                if "Error:" in paths_result.stdout:
                    return []
                    
                paths = paths_result.stdout.strip().split(", ")
                return [f for f in paths if f and os.path.exists(f) and os.path.isfile(f)]
            
            return []
        except Exception as e:
            print(f"Error getting clipboard files: {e}")
            return []

    def read_file_content(file_path):
        """Read file content and encode it in base64 for transmission"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return base64.b64encode(content).decode('utf-8')
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def prepare_file_data(file_path):
        """Prepare a file for transmission to the server"""
        content = read_file_content(file_path)
        if content is not None:
            return {
                'name': os.path.basename(file_path),
                'content': content
            }
        return None

    try:
        while True:
            # Check for clipboard content changes
            current_content = pyperclip.paste()
            current_files = set(get_clipboard_files())
            
            if current_content != last_content or current_files != last_files:
                if current_files:
                    # Send file (only the first one if multiple files)
                    file_data = prepare_file_data(next(iter(current_files)))
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
                    # Send text content
                    try:
                        response = requests.post(
                            f"{server_url}/clipboard",
                            json={'type': 'text', 'content': current_content}
                        )
                        if response.status_code == 200:
                            print(f"Sent text: {current_content[:50]}...")
                    except requests.exceptions.RequestException as e:
                        print(f"Error sending text: {e}")
                
                # Update last known content
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