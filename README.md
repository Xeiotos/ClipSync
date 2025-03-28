# ClipSync - Simple One-Way Clipboard Sharing

A simple tool to share clipboard content from a MacBook to a Windows desktop over a local network. Supports text and single file transfers.

## Features
- Share text from MacBook to Windows
- Share single files from MacBook to Windows
- Works over local network
- No installation required (just Python)
- Automatic file cleanup on Windows

## Requirements

### MacBook (Client)
- Python 3.7 or higher
- For file support:
  - macOS (for clipboard file handling)
  - `osascript` (pre-installed on macOS)

### Windows (Server)
- Python 3.7 or higher
- PowerShell (for clipboard operations)

## Setup

1. Install Python 3.7 or higher on both machines if not already installed
2. Clone or download this repository on both machines
3. Set up the virtual environment:

   On MacBook:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   On Windows:
   ```bash
   setup.bat
   ```

   This will create a `.venv` directory and install all required dependencies in the virtual environment.

## Usage

### On Windows (Server)
1. Open a terminal/command prompt
2. Navigate to the project directory
3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate.bat
   ```
4. Run the server:
   ```bash
   python server.py
   ```
5. Note the IP address and port shown in the console (e.g., http://192.168.1.100:5000)

### On MacBook (Client)
1. Open a terminal
2. Navigate to the project directory
3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
4. Run the client with the server's URL:
   ```bash
   python client.py http://<windows-ip>:5000
   ```
   Replace `<windows-ip>` with the IP address shown in the Windows console

## How it Works

### Text Sharing
- Copy text on MacBook (Cmd+C)
- The text will automatically be copied to the Windows clipboard
- Paste on Windows (Ctrl+V)

### File Sharing
- Copy a single file on MacBook (Cmd+C)
- The client uses macOS's clipboard API to get the file reference
- The file content is read and sent to the Windows server
- The file is stored in `%TEMP%\clipsync` on Windows
- The file is automatically copied to the Windows clipboard
- You can then paste the file wherever you want

## Notes
- Both machines must be on the same local network
- The Windows machine must have the server running to receive clipboard content
- The MacBook must have the client running to send clipboard content
- Always make sure the virtual environment is activated before running the scripts
- Only single files are supported (no directories or multiple files)
- Previous files are automatically cleaned up when new ones are copied
- File sharing requires proper permissions and sufficient disk space
- The Windows firewall may need to be configured to allow incoming connections on port 5000 