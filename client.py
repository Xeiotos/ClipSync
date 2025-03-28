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
        try:
            # Check if clipboard has files
            check_script = '''
            set cbInfo to (clipboard info) as string
            if cbInfo contains "«class furl»" then
                return "has_files"
            else
                return "no_files"
            end if
            '''
            
            check_result = subprocess.run(['osascript', '-e', check_script], capture_output=True, text=True)
            
            if check_result.stdout.strip() == "has_files":
                # Try to get file path directly from pbpaste
                pbpaste_cmd = ['pbpaste', '-Prefer', 'txt']
                pbpaste_result = subprocess.run(pbpaste_cmd, capture_output=True, text=True)
                
                # If pbpaste returns a file path, use it
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
                        
                    # Process the paths
                    paths = paths_result.stdout.strip().split(", ")
                    valid_files = [f for f in paths if f and os.path.exists(f) and os.path.isfile(f)]
                    return valid_files
            
            return []
        except Exception as e:
            print(f"Error getting clipboard files: {e}")
            return []

    def read_file_content(file_path):
        try:
            # Read file content directly
            with open(file_path, 'rb') as f:
                content = f.read()
                return base64.b64encode(content).decode('utf-8')
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
    
    def is_file_extension(text):
        """Check if the text looks like a filename with extension"""
        text = text.strip().lower()
        common_extensions = ['.pdf', '.txt', '.doc', '.docx', '.jpg', '.png', '.xls', '.xlsx', '.ppt', '.pptx']
        return any(text.endswith(ext) for ext in common_extensions)

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
                elif current_content.strip() and not is_file_extension(current_content):
                    # Only send text if it doesn't look like a filename
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