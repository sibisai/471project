import socket
import os
import time

# Configuration
SERVER_HOST = "127.0.0.1"
CONTROL_PORT = 5001
CHUNK_SIZE = 4096
DOWNLOAD_DIR = "client_downloads"

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def recv_line(sock):
    """Helper function to receive a line of text until newline"""
    buffer = b""
    while b"\n" not in buffer:
        try:
            chunk = sock.recv(1)
            if not chunk:
                break
            buffer += chunk
        except Exception as e:
            print(f"Error receiving line: {e}")
            break
    return buffer.decode('utf-8').strip()

def upload_file(control_sock, filepath):
    """Upload a file to the server"""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found!")
        return
    
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)
    
    print(f"\n=== UPLOADING FILE ===")
    print(f"File: {filename}")
    print(f"Size: {filesize} bytes")
    
    try:
        # Send upload command on control connection
        header = f"UPLOAD {filename} {filesize}\n"
        control_sock.sendall(header.encode())
        
        # Wait for OK with data port from server
        response = recv_line(control_sock)
        if not response.startswith("OK"):
            print(f"Server error: {response}")
            return
        
        data_port = int(response.split()[1])
        
        # Small delay to ensure server data socket is ready
        time.sleep(0.1)
        
        # Connect to data port
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.connect((SERVER_HOST, data_port))
        
        # Send file in chunks with progress indicator
        with open(filepath, 'rb') as f:
            sent = 0
            while sent < filesize:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                data_sock.sendall(chunk)
                sent += len(chunk)
                percent = (sent * 100) // filesize
                print(f"\rUploading: {percent}% [{sent}/{filesize} bytes]", end="")
        
        data_sock.close()
        
        # Wait for DONE from server on control connection
        response = recv_line(control_sock)
        if response == "DONE":
            print(f"\n✓ Upload complete!")
        else:
            print(f"\nServer response: {response}")
    
    except Exception as e:
        print(f"\n✗ Upload failed: {e}")

def download_file(control_sock, filename):
    """Download a file from the server"""
    print(f"\n=== DOWNLOADING FILE ===")
    print(f"File: {filename}")
    
    try:
        # Send download command on control connection
        header = f"DOWNLOAD {filename}\n"
        control_sock.sendall(header.encode())
        
        # Read response
        response = recv_line(control_sock)
        
        if response.startswith("ERROR"):
            print(f"✗ {response}")
            return
        
        # Parse file size and data port from "OK <filesize> <data_port>"
        if response.startswith("OK"):
            parts = response.split()
            filesize = int(parts[1])
            data_port = int(parts[2])
            print(f"Size: {filesize} bytes")
        else:
            print(f"Unexpected response: {response}")
            return
        
        # Send READY signal on control connection
        control_sock.sendall(b"READY\n")
        
        # Small delay to ensure server data socket is ready
        time.sleep(0.1)
        
        # Connect to data port
        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_sock.connect((SERVER_HOST, data_port))
        
        # Prepare local file path
        local_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Ensure download directory exists (defensive)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Receive file in chunks with progress indicator
        with open(local_path, 'wb') as f:
            received = 0
            while received < filesize:
                chunk = data_sock.recv(min(CHUNK_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                percent = (received * 100) // filesize
                print(f"\rDownloading: {percent}% [{received}/{filesize} bytes]", end="")
        
        data_sock.close()
        
        # Wait for DONE from server on control connection
        response = recv_line(control_sock)
        if response == "DONE":
            print(f"\n✓ Download complete! Saved to: {local_path}")
        else:
            print(f"\nServer response: {response}")
    
    except Exception as e:
        print(f"\n✗ Download failed: {e}")

def list_files(control_sock):
    """List available files on the server"""
    print(f"\n=== AVAILABLE FILES ===")
    
    try:
        # Send list command on control connection
        control_sock.sendall(b"LIST\n")
        
        # Wait for OK from server
        response = recv_line(control_sock)
        if response != "OK":
            print(f"Server error: {response}")
            return
        
        # Receive file list
        files = []
        while True:
            line = recv_line(control_sock)
            if line == "DONE":
                break
            files.append(line)
        
        # Display files
        if files:
            for i, filename in enumerate(files, 1):
                print(f"{i}. {filename}")
        else:
            print("No files available on server.")
    
    except Exception as e:
        print(f"\n✗ List failed: {e}")

def main_menu():
    """Display interactive menu"""
    print("\n" + "="*50)
    print("     FILE TRANSFER CLIENT")
    print("="*50)
    print("\n1. Upload a file")
    print("2. Download a file")
    print("3. List available files")
    print("4. Exit")
    print()

def main():
    """Main client loop"""
    try:
        # Establish persistent control connection
        control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_sock.connect((SERVER_HOST, CONTROL_PORT))
        print(f"Connected to server at {SERVER_HOST}:{CONTROL_PORT}")
        
        while True:
            main_menu()
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                filepath = input("\nEnter the path of file to upload: ").strip()
                upload_file(control_sock, filepath)
            
            elif choice == "2":
                filename = input("\nEnter the filename to download: ").strip()
                download_file(control_sock, filename)
            
            elif choice == "3":
                list_files(control_sock)
            
            elif choice == "4":
                # Send QUIT command
                control_sock.sendall(b"QUIT\n")
                response = recv_line(control_sock)
                print("\nGoodbye!")
                break
            
            else:
                print("\n✗ Invalid choice. Please enter 1, 2, 3, or 4.")
            
            input("\nPress Enter to continue...")
        
        control_sock.close()
    
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()