# ClipSync - Simple One-Way Clipboard Sharing

A simple tool to share clipboard content from a MacBook to a Windows desktop over a local network. Supports both text and files/folders.

## Features
- Share text from MacBook to Windows
- Share files and folders from MacBook to Windows
- Works over local network
- No installation required (just Python)
- Automatic file cleanup on Windows

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

### File/Folder Sharing
- Copy files or folders on MacBook (Cmd+C)
- Files will be automatically transferred to the Windows temp directory
- The files are stored in `%TEMP%\clipsync` on Windows
- Previous files are automatically cleaned up when new files are copied
- You can then copy the files from the temp directory to wherever you want

## Notes
- Both machines must be on the same local network
- The Windows machine must have the server running to receive clipboard content
- The MacBook must have the client running to send clipboard content
- Always make sure the virtual environment is activated before running the scripts
- For file sharing, ensure you have sufficient disk space in the Windows temp directory
- The server automatically cleans up previous files when new ones are copied 