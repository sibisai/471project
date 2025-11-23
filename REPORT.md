# File Transfer Application - Technical Report

## Project Overview

This report documents the design and implementation of a Python-based file transfer application using TCP sockets. The application follows an FTP-like architecture with separate control and data connections, demonstrating fundamental networking concepts including socket programming, multi-threading, and reliable data transfer protocols.

---

## Architecture Design

### Two-Connection Model

Our implementation uses a **two-connection architecture** similar to FTP (File Transfer Protocol):

1. **Control Connection (Port 5001)**

   - Persistent connection that remains open throughout the client session
   - Handles all commands: UPLOAD, DOWNLOAD, LIST, QUIT
   - Sends acknowledgments and status messages
   - Lightweight text-based protocol

2. **Data Connection (Port 5002)**
   - Temporary connection opened only during file transfers
   - Handles binary file data transmission
   - Closes immediately after each transfer completes
   - Separates control plane from data plane for better performance

**Design Rationale:**

- **Separation of Concerns:** Commands and data flow through different channels, preventing command confusion during large transfers
- **Performance:** Data transfers don't block command processing
- **Scalability:** Control connection can manage multiple sequential transfers without reconnecting
- **Real-world Pattern:** Mirrors industry-standard FTP architecture, demonstrating understanding of established protocols

---

## Protocol Design

### Command Structure

All commands follow a simple text-based format with newline delimiters:

```
UPLOAD <filename> <filesize>\n
DOWNLOAD <filename>\n
LIST\n
QUIT\n
```

### Upload Flow

```
1. [Control] Client sends: UPLOAD filename filesize\n
2. [Control] Server responds: OK data_port\n
3. [Data]    Client connects to data_port and streams file
4. [Control] Server sends: DONE\n (acknowledges completion)
```

**Key Design Decisions:**

- Server tells client which data port to use (flexibility for future load balancing)
- File size sent upfront allows server to allocate resources and validate completion
- Acknowledgment on control channel confirms successful receipt

### Download Flow

```
1. [Control] Client sends: DOWNLOAD filename\n
2. [Control] Server responds: OK filesize data_port\n
3. [Control] Client sends: READY\n
4. [Data]    Client connects to data_port
5. [Data]    Server streams file to client
6. [Control] Server sends: DONE\n
```

**Key Design Decisions:**

- Server sends file size first so client can allocate buffer and track progress
- READY signal ensures client is prepared before data transfer begins
- Error handling: Server sends "ERROR FileNotFound" if file doesn't exist

---

## Implementation Details

### Server Architecture (server.py)

**Multi-threading Model:**

- Main thread listens for control connections on port 5001
- Each client gets a dedicated handler thread (`handle_client`)
- Data transfers spawn additional threads (`handle_data_connection`)
- Supports multiple simultaneous clients without blocking

**File Storage:**

- Local directory: `server_files/`
- Automatically created if missing (`os.makedirs`)
- Files identified by name only (simple flat structure)

**Error Handling:**

- Try-catch blocks around socket operations
- Timeout on data connections (10 seconds) prevents indefinite blocking
- Graceful handling of missing files and connection failures

### Client Architecture (client.py)

**Connection Management:**

- Single persistent control connection established at startup
- Temporary data connections for each file transfer
- Clean shutdown with QUIT command

**User Interface:**

- Interactive menu system (1-4 options)
- Real-time progress indicators showing percentage and bytes transferred
- Clear success/error messages

**Progress Tracking:**

```python
percent = (sent * 100) // filesize
print(f"\rUploading: {percent}% [{sent}/{filesize} bytes]", end="")
```

---

## Chunked Transfer Mechanism

**Chunk Size:** 4096 bytes (4KB)

**Why 4KB?**

- Balance between memory efficiency and transfer speed
- Standard page size on most operating systems
- Reduces overhead while maintaining reasonable buffer size

**Upload Process:**

```python
with open(filepath, 'rb') as f:
    sent = 0
    while sent < filesize:
        chunk = f.read(CHUNK_SIZE)
        data_sock.sendall(chunk)
        sent += len(chunk)
```

**Download Process:**

```python
with open(local_path, 'wb') as f:
    received = 0
    while received < filesize:
        chunk = data_sock.recv(min(CHUNK_SIZE, filesize - received))
        f.write(chunk)
        received += len(chunk)
```

**Benefits:**

- Handles files of any size (no memory constraints)
- Allows progress tracking
- Network-friendly (doesn't overwhelm buffers)
- Binary-safe (preserves file integrity for images, PDFs, etc.)

---

## Reliability Mechanisms

### Acknowledgments

- **OK:** Server ready to proceed
- **DONE:** Transfer completed successfully
- **ERROR:** Operation failed (with reason)

### TCP Guarantees

- In-order delivery (no packet reordering needed)
- Retransmission of lost packets (built into TCP)
- Flow control (TCP handles congestion)

### Application-Level Validation

- File size comparison (sent vs received)
- Binary mode file operations (prevents data corruption)

---

## Concurrency & Multi-Client Support

**Threading Model:**

```python
thread = threading.Thread(target=handle_client, args=(conn, addr))
thread.start()
```

**Benefits:**

- Multiple clients can connect simultaneously
- Each client has isolated state
- Non-blocking operations

**Thread Safety:**

- File I/O operations are independent (different files/connections)
- No shared state between client handlers
- Simple design avoids race conditions

---

## Testing & Validation

**Test Cases Implemented:**

1. ✅ Upload small text file (10 bytes)
2. ✅ Upload binary file (image, PDF)
3. ✅ Download files and verify integrity (checksum comparison)
4. ✅ List available files
5. ✅ Error handling (missing files, invalid paths)
6. ✅ Multiple simultaneous clients

**Progress Indicator Testing:**

- Added artificial delays (`time.sleep(1)`) to visualize chunked transfers
- Verified progress updates correctly for various file sizes

---

## Design Trade-offs

### Chosen Approach: Two Separate Ports

**Pros:**

- Clear separation of control and data
- Mirrors FTP standard
- Easier to debug (can monitor ports independently)

**Cons:**

- Requires two ports open on firewall
- Slightly more complex than single-connection design

### Alternative Considered: Multiplexing on Single Port

**Pros:**

- Only one port needed
- Simpler firewall configuration

**Cons:**

- More complex protocol (need message framing)
- Commands could be delayed during large transfers
- Less aligned with industry standards

**Decision:** Chose two-connection model to demonstrate understanding of real-world protocols and proper architecture patterns.

---

## Challenges & Solutions

### Challenge 1: Race Condition in Data Connection

**Problem:** Client tried to connect to data port before server was ready to accept.

**Solution:** Added 100ms delay (`time.sleep(0.1)`) after server sends data port number, giving server time to set up listener socket.

### Challenge 2: Binary File Integrity

**Problem:** Initial design opened files in text mode, corrupting binary data.

**Solution:** Used binary mode (`'rb'`, `'wb'`) for all file operations, preserving exact byte sequences.

### Challenge 3: Progress Indicator for Small Files

**Problem:** Transfers completed instantly, making progress invisible.

**Solution:** Documented testing procedure with artificial delays for demonstration purposes.

---

## Future Enhancements (Phase 2 & 3)

### Phase 2: AWS Deployment

- Deploy server.py to EC2 instance
- Update `SERVER_HOST` in client.py to EC2 public IP
- Configure security groups for ports 5001 and 5002

### Phase 3: Cloud-Native Features

- **S3 Integration:** Store files in S3 bucket instead of local directory
- **Load Balancing:** Multiple EC2 instances behind Elastic Load Balancer
- **Monitoring:** CloudWatch metrics for transfer speed and error rates
- **Authentication:** Add user login before allowing transfers

---

## Conclusion

This implementation successfully demonstrates:

- ✅ Two-connection FTP-like architecture
- ✅ Reliable TCP socket programming
- ✅ Multi-threaded server handling concurrent clients
- ✅ Chunked file transfer with progress tracking
- ✅ Proper error handling and acknowledgments
- ✅ Binary file support with integrity preservation

The design prioritizes **clarity**, **reliability**, and **adherence to real-world protocols**, providing a solid foundation for cloud deployment in future phases.

---

## References

- Python Socket Programming Documentation: https://docs.python.org/3/library/socket.html
- FTP Protocol (RFC 959): https://tools.ietf.org/html/rfc959
- TCP/IP Protocol Suite: Forouzan, Behrouz A. (Textbook reference)
