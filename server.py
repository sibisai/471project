import socket
import threading
import os
# import time

# Configuration
HOST = "0.0.0.0"
PORT = 5001
STORAGE_DIR = "server_files"
CHUNK_SIZE = 4096

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

def recv_line(conn):
    """Helper function to receive a line of text until newline"""
    buffer = b""
    while b"\n" not in buffer:
        try:
            chunk = conn.recv(1)
            if not chunk:
                break
            buffer += chunk
        except Exception as e:
            print(f"Error receiving line: {e}")
            break
    return buffer.decode('utf-8').strip()

def handle_client(conn, addr):
    """Handle individual client connection"""
    print(f"[NEW CONNECTION] {addr} connected")
    
    try:
        # Receive command line
        cmd_line = recv_line(conn)
        if not cmd_line:
            return
        
        parts = cmd_line.split()
        command = parts[0]
        
        if command == "UPLOAD":
            # Parse upload request
            filename = parts[1]
            filesize = int(parts[2])
            filepath = os.path.join(STORAGE_DIR, filename)
            
            print(f"[UPLOAD] Receiving {filename} ({filesize} bytes) from {addr}")
            
            # Send OK acknowledgment
            conn.sendall(b"OK\n")
            
            # Ensure storage directory exists (defensive)
            os.makedirs(STORAGE_DIR, exist_ok=True)
            
            # Receive file data in chunks
            with open(filepath, 'wb') as f:
                received = 0
                while received < filesize:
                    chunk = conn.recv(min(CHUNK_SIZE, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    # time.sleep(1)
            
            # Send DONE acknowledgment
            conn.sendall(b"DONE\n")
            print(f"[UPLOAD] Complete: {filename} saved ({received} bytes)")
        
        elif command == "DOWNLOAD":
            # Parse download request
            filename = parts[1]
            filepath = os.path.join(STORAGE_DIR, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                conn.sendall(b"ERROR FileNotFound\n")
                print(f"[DOWNLOAD] File not found: {filename} requested by {addr}")
                return
            
            # Get file size
            filesize = os.path.getsize(filepath)
            print(f"[DOWNLOAD] Sending {filename} ({filesize} bytes) to {addr}")
            
            # Send OK with file size
            conn.sendall(f"OK {filesize}\n".encode())
            
            # Wait for READY signal
            ready = recv_line(conn)
            if ready != "READY":
                print(f"[DOWNLOAD] Client not ready, aborting")
                return
            
            # Send file data in chunks
            with open(filepath, 'rb') as f:
                sent = 0
                while sent < filesize:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    conn.sendall(chunk)
                    sent += len(chunk)
                    # time.sleep(1)
            
            # Send DONE acknowledgment
            conn.sendall(b"DONE\n")
            print(f"[DOWNLOAD] Complete: {filename} sent ({sent} bytes)")
        
        else:
            conn.sendall(b"ERROR UnknownCommand\n")
            print(f"[ERROR] Unknown command from {addr}: {command}")
    
    except Exception as e:
        print(f"[ERROR] Exception handling client {addr}: {e}")
    
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    """Start the TCP server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    print(f"[STORAGE] Files will be stored in: {os.path.abspath(STORAGE_DIR)}")
    print("[READY] Waiting for connections...")
    
    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()