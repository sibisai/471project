import socket
import threading
import os
# import time

# Configuration
HOST = "0.0.0.0"
CONTROL_PORT = 5001
DATA_PORT = 5002
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

def handle_data_connection(operation, filename, filesize, addr):
    """Handle data connection for file transfers"""
    try:
        # Create data socket and wait for client connection
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        data_socket.bind((HOST, DATA_PORT))
        data_socket.listen(1)
        data_socket.settimeout(10)  # 10 second timeout
        
        data_conn, data_addr = data_socket.accept()
        
        if operation == "UPLOAD":
            filepath = os.path.join(STORAGE_DIR, filename)
            
            # Ensure storage directory exists (defensive)
            os.makedirs(STORAGE_DIR, exist_ok=True)
            
            # Receive file data in chunks
            with open(filepath, 'wb') as f:
                received = 0
                while received < filesize:
                    chunk = data_conn.recv(min(CHUNK_SIZE, filesize - received))
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)
                    # time.sleep(1)
            
            print(f"[UPLOAD] Complete: {filename} saved ({received} bytes)")
        
        elif operation == "DOWNLOAD":
            filepath = os.path.join(STORAGE_DIR, filename)
            
            # Send file data in chunks
            with open(filepath, 'rb') as f:
                sent = 0
                filesize = os.path.getsize(filepath)
                while sent < filesize:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    data_conn.sendall(chunk)
                    sent += len(chunk)
                    # time.sleep(1)
            
            print(f"[DOWNLOAD] Complete: {filename} sent ({sent} bytes)")
        
        data_conn.close()
        data_socket.close()
        
    except socket.timeout:
        print(f"[ERROR] Data connection timeout for {operation} {filename}")
    except Exception as e:
        print(f"[ERROR] Data connection error: {e}")

def handle_client(conn, addr):
    """Handle individual client control connection"""
    print(f"[NEW CONNECTION] {addr} connected")
    
    try:
        while True:
            # Receive command line
            cmd_line = recv_line(conn)
            if not cmd_line:
                break
            
            parts = cmd_line.split()
            command = parts[0]
            
            if command == "UPLOAD":
                # Parse upload request
                filename = parts[1]
                filesize = int(parts[2])
                
                print(f"[UPLOAD] Receiving {filename} ({filesize} bytes) from {addr}")
                
                # Send OK with data port
                conn.sendall(f"OK {DATA_PORT}\n".encode())
                
                # Start data connection handler in separate thread
                data_thread = threading.Thread(
                    target=handle_data_connection,
                    args=("UPLOAD", filename, filesize, addr)
                )
                data_thread.start()
                data_thread.join()  # Wait for transfer to complete
                
                # Send DONE acknowledgment on control connection
                conn.sendall(b"DONE\n")
            
            elif command == "DOWNLOAD":
                # Parse download request
                filename = parts[1]
                filepath = os.path.join(STORAGE_DIR, filename)
                
                # Check if file exists
                if not os.path.exists(filepath):
                    conn.sendall(b"ERROR FileNotFound\n")
                    print(f"[DOWNLOAD] File not found: {filename} requested by {addr}")
                    continue
                
                # Get file size
                filesize = os.path.getsize(filepath)
                print(f"[DOWNLOAD] Sending {filename} ({filesize} bytes) to {addr}")
                
                # Send OK with filesize and data port
                conn.sendall(f"OK {filesize} {DATA_PORT}\n".encode())
                
                # Wait for READY signal
                ready = recv_line(conn)
                if ready != "READY":
                    print(f"[DOWNLOAD] Client not ready, aborting")
                    continue
                
                # Start data connection handler in separate thread
                data_thread = threading.Thread(
                    target=handle_data_connection,
                    args=("DOWNLOAD", filename, filesize, addr)
                )
                data_thread.start()
                data_thread.join()  # Wait for transfer to complete
                
                # Send DONE acknowledgment on control connection
                conn.sendall(b"DONE\n")
            
            elif command == "LIST":
                # List available files (uses control connection for small data)
                print(f"[LIST] Sending file list to {addr}")
                
                # Send OK acknowledgment
                conn.sendall(b"OK\n")
                
                # Get list of files in storage directory
                files = os.listdir(STORAGE_DIR)
                
                # Send each filename
                for filename in files:
                    conn.sendall(f"{filename}\n".encode())
                
                # Send DONE acknowledgment
                conn.sendall(b"DONE\n")
                print(f"[LIST] Complete: Sent {len(files)} filenames")
            
            elif command == "QUIT":
                print(f"[QUIT] Client {addr} disconnecting")
                conn.sendall(b"OK\n")
                break
            
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
    server_socket.bind((HOST, CONTROL_PORT))
    server_socket.listen(5)
    
    print(f"[LISTENING] Control connection on {HOST}:{CONTROL_PORT}")
    print(f"[LISTENING] Data connection on {HOST}:{DATA_PORT}")
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