# ClipSync - Simple One-Way Clipboard Sharing

A simple tool to share clipboard content from a MacBook to a Windows desktop over a local network.

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
- The Windows machine runs a server that listens for clipboard content
- The MacBook runs a client that monitors the clipboard and sends changes to the server
- When you copy text on the MacBook, it will automatically be copied to the Windows clipboard
- The client checks for clipboard changes every 500ms
- Press Ctrl+C on either machine to stop the respective script

## Notes
- Both machines must be on the same local network
- This tool only works with text content
- The Windows machine must have the server running to receive clipboard content
- The MacBook must have the client running to send clipboard content
- Always make sure the virtual environment is activated before running the scripts 