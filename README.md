# File Transfer Application - Phase 1

A simple Python client-server file transfer application using TCP sockets with chunked transfers and progress bars.

---

## 📁 Project Structure

```
project/
│
├── server.py              # TCP server for handling file uploads/downloads
├── client.py              # Interactive client for transferring files
├── README.md              # This file
│
├── server_files/          # Server storage (created automatically)
│   └── (uploaded files stored here)
│
├── client_downloads/      # Client downloads (created automatically)
│   └── (downloaded files saved here)
│
└── test_files/            # Test files (you create these)
    ├── small.txt
    ├── medium.jpg
    └── large.pdf
```

---

## ⚙️ Requirements

- **Python 3.7+** (no external libraries needed)
- **Operating System**: Windows, macOS, or Linux

---

## 🚀 Setup Instructions

### 1. Create Project Directory

```bash
mkdir project
cd project
```

### 2. Create the Files

Save the following files in your project directory:

- `server.py` - The server code
- `client.py` - The client code
- `README.md` - This documentation

### 3. Create Test Files (Optional)

Create a `test_files/` directory with some sample files:

```bash
mkdir test_files
```

Or use any existing files you want to test with (images, PDFs, etc.)

---

## 🧪 How to Run & Test

### Step 1: Start the Server

Open a terminal and run:

```bash
python server.py
```

**Expected output:**

```
[LISTENING] Server is listening on 0.0.0.0:5001
[STORAGE] Files will be stored in: /path/to/server_files
[READY] Waiting for connections...
```

Keep this terminal open - the server is now running!

---

### Step 2: Start the Client

Open a **second terminal** (keep the server running) and run:

```bash
python client.py
```

**Expected output:**

```
==================================================
     FILE TRANSFER CLIENT
==================================================

1. Upload a file
2. Download a file
3. Exit

Enter your choice (1-3):
```

---

## 📤 Test Case 1: Upload a File

1. In the client menu, type `1` and press Enter
2. Enter the path to a test file:
   ```
   Enter the path of file to upload: test_files/small.txt
   ```
3. Watch the progress bar:

   ```
   === UPLOADING FILE ===
   File: small.txt
   Size: 28 bytes
   Uploading: 100% [28/28 bytes]
   ✓ Upload complete!
   ```

4. Check the server terminal - you should see:

   ```
   [NEW CONNECTION] ('127.0.0.1', 54321) connected
   [UPLOAD] Receiving small.txt (28 bytes) from ('127.0.0.1', 54321)
   [UPLOAD] Complete: small.txt saved (28 bytes)
   [DISCONNECTED] ('127.0.0.1', 54321)
   ```

5. Verify the file exists:
   ```bash
   ls server_files/
   # Should show: small.txt
   ```

---

## 📥 Test Case 2: Download a File

1. In the client menu, type `2` and press Enter
2. Enter the filename to download:
   ```
   Enter the filename to download: small.txt
   ```
3. Watch the progress bar:

   ```
   === DOWNLOADING FILE ===
   File: small.txt
   Size: 28 bytes
   Downloading: 100% [28/28 bytes]
   ✓ Download complete! Saved to: client_downloads/small.txt
   ```

4. Verify the downloaded file:

   ```bash
   ls client_downloads/
   # Should show: small.txt

   cat client_downloads/small.txt
   # Should show: Test file
   ```

---

## 📋 Test Case 3: Multiple File Types

Test with different file types to ensure binary transfers work:

**Upload an image:**

```
Enter the path of file to upload: test_files/photo.jpg
```

**Download it back:**

```
Enter the filename to download: photo.jpg
```

**Verify integrity:**

```bash
# Compare checksums (Linux/macOS)
md5sum test_files/photo.jpg
md5sum client_downloads/photo.jpg
# Should match!
```

---

## 🔄 Test Case 4: Multiple Clients

**Note:** With small files, transfers complete instantly, so you'll only see `[ACTIVE CONNECTIONS] 1`. To properly test multi-client support and see the progress bar in action, add artificial delays.

### Option A: Add Artificial Delay (Recommended for Testing)

Temporarily modify `server.py` to slow down transfers:

1. Ensure `import time` is uncommented at the top

2. In the **UPLOAD** section, uncomment delay after receiving each chunk:

   ```python
   # Inside the while loop for uploads (around line 65)
   f.write(chunk)
   received += len(chunk)
   time.sleep(1)  # Add 1 second delay per chunk
   ```

3. In the **DOWNLOAD** section, uncomment delay after sending each chunk:

   ```python
   # Inside the while loop for downloads (around line 104)
   conn.sendall(chunk)
   sent += len(chunk)
   time.sleep(1)  # Add 1 second delay per chunk
   ```

4. Now test with multiple clients:

   - Keep the server running
   - Open **3 separate terminals** and run `python client.py` in each
   - Start uploading/downloading from each terminal quickly
   - Watch the server show: `[ACTIVE CONNECTIONS] 3`
   - See the progress bars slowly update in each client (instead of instantly jumping to 100%)

5. **Remove the `time.sleep()` lines after testing!**

### Option B: Use Large Files

Create a very large file for testing

Then upload from multiple terminals - the transfers will be slow enough to see simultaneous connections.

---

## 🧹 Test Case 5: Error Handling

### Download Non-Existent File:

```

Enter the filename to download: doesnotexist.txt

Expected output:
✗ ERROR FileNotFound

```

### Upload Non-Existent File:

```

Enter the path of file to upload: fake.txt

Expected output:
Error: File 'fake.txt' not found!

```

---

## ⚙️ Configuration

You can modify these settings at the top of each file:

**server.py:**

```python
HOST = "0.0.0.0"          # Listen on all interfaces
PORT = 5001               # Server port
STORAGE_DIR = "server_files"  # Where to store uploads
CHUNK_SIZE = 4096         # 4KB chunks
```

**client.py:**

```python
SERVER_HOST = "127.0.0.1"  # Server address (localhost)
SERVER_PORT = 5001         # Server port
CHUNK_SIZE = 4096          # 4KB chunks
DOWNLOAD_DIR = "client_downloads"  # Where to save downloads
```

---

## 🛑 Stopping the Server

Press `Ctrl+C` in the server terminal:

```
^C
[SHUTDOWN] Server shutting down...
```

---

## ✅ Expected Behavior Summary

| Action                | Expected Result                                                     |
| --------------------- | ------------------------------------------------------------------- |
| Upload file           | Progress bar → "✓ Upload complete!" → File in `server_files/`       |
| Download file         | Progress bar → "✓ Download complete!" → File in `client_downloads/` |
| Download missing file | "✗ ERROR FileNotFound"                                              |
| Upload missing file   | "Error: File not found!"                                            |
| Multiple clients      | Server handles all simultaneously                                   |
| File integrity        | Uploaded and downloaded files are identical                         |

---

## 🐛 Troubleshooting

**"Address already in use" error:**

- Wait 30 seconds for the port to release, or restart your computer
- Change `PORT = 5001` to a different number (e.g., `5002`)

**"Connection refused" error:**

- Make sure the server is running first
- Check that `SERVER_HOST` and `SERVER_PORT` match in client.py

**Files corrupt after transfer:**

- Check that both `CHUNK_SIZE` values match
- Ensure files are opened in binary mode (`'rb'` and `'wb'`)

---

## 📝 Protocol Details

**Upload Flow:**

```
Client → Server: UPLOAD filename filesize\n
Server → Client: OK\n
Client → Server: [binary file data in chunks]
Server → Client: DONE\n
```

**Download Flow:**

```
Client → Server: DOWNLOAD filename\n
Server → Client: OK filesize\n
Client → Server: READY\n
Server → Client: [binary file data in chunks]
Server → Client: DONE\n
```

---

## 🎯 Phase 1 Completed:

Working local file transfer system with:

- ✅ TCP client-server architecture
- ✅ Multi-client support (threading)
- ✅ Chunked file transfers
- ✅ Progress bars
- ✅ Basic ACK protocol
- ✅ Upload and download functionality

**Next Phase:** Deploy to AWS EC2 and enable remote file transfers
