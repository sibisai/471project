import socket
import os

# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
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

def upload_file(filepath):
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
        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))
        
        # Send upload command
        header = f"UPLOAD {filename} {filesize}\n"
        s.sendall(header.encode())
        
        # Wait for OK from server
        response = recv_line(s)
        if response != "OK":
            print(f"Server error: {response}")
            return
        
        # Send file in chunks with progress bar
        with open(filepath, 'rb') as f:
            sent = 0
            while sent < filesize:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                s.sendall(chunk)
                sent += len(chunk)
                percent = (sent * 100) // filesize
                print(f"\rUploading: {percent}% [{sent}/{filesize} bytes]", end="")
        
        # Wait for DONE from server
        response = recv_line(s)
        if response == "DONE":
            print(f"\n✓ Upload complete!")
        else:
            print(f"\nServer response: {response}")
        
        s.close()
    
    except Exception as e:
        print(f"\n✗ Upload failed: {e}")

def download_file(filename):
    """Download a file from the server"""
    print(f"\n=== DOWNLOADING FILE ===")
    print(f"File: {filename}")
    
    try:
        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))
        
        # Send download command
        header = f"DOWNLOAD {filename}\n"
        s.sendall(header.encode())
        
        # Read response
        response = recv_line(s)
        
        if response.startswith("ERROR"):
            print(f"✗ {response}")
            s.close()
            return
        
        # Parse file size from "OK <filesize>"
        if response.startswith("OK"):
            filesize = int(response.split()[1])
            print(f"Size: {filesize} bytes")
        else:
            print(f"Unexpected response: {response}")
            s.close()
            return
        
        # Send READY signal
        s.sendall(b"READY\n")
        
        # Prepare local file path
        local_path = os.path.join(DOWNLOAD_DIR, filename)
        
        # Ensure download directory exists (defensive)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Receive file in chunks with progress bar
        with open(local_path, 'wb') as f:
            received = 0
            while received < filesize:
                chunk = s.recv(min(CHUNK_SIZE, filesize - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                percent = (received * 100) // filesize
                print(f"\rDownloading: {percent}% [{received}/{filesize} bytes]", end="")
        
        # Wait for DONE from server
        response = recv_line(s)
        if response == "DONE":
            print(f"\n✓ Download complete! Saved to: {local_path}")
        else:
            print(f"\nServer response: {response}")
        
        s.close()
    
    except Exception as e:
        print(f"\n✗ Download failed: {e}")

def list_files():
    """List available files on the server"""
    print(f"\n=== AVAILABLE FILES ===")
    
    try:
        # Connect to server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))
        
        # Send list command
        s.sendall(b"LIST\n")
        
        # Wait for OK from server
        response = recv_line(s)
        if response != "OK":
            print(f"Server error: {response}")
            s.close()
            return
        
        # Receive file list
        files = []
        while True:
            line = recv_line(s)
            if line == "DONE":
                break
            files.append(line)
        
        # Display files
        if files:
            for i, filename in enumerate(files, 1):
                print(f"{i}. {filename}")
        else:
            print("No files available on server.")
        
        s.close()
    
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
    while True:
        main_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            filepath = input("\nEnter the path of file to upload: ").strip()
            upload_file(filepath)
        
        elif choice == "2":
            filename = input("\nEnter the filename to download: ").strip()
            download_file(filename)
        
        elif choice == "3":
            list_files()
        
        elif choice == "4":
            print("\nGoodbye!")
            break
        
        else:
            print("\n✗ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()