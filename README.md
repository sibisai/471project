# File Transfer Application - Phase 1

## 👥 Team Members

- Andrew Chang - ankechang2752@csu.fullerton.edu
- Hyndavi Teegela - Hyndavi.teegela@csu.fullerton.edu
- Jenny Phan - Jphan131@csu.fullerton.edu
- Jason Luu - jluu6324@csu.fullerton.edu
- Sibi Ukeshkumar - sibi@csu.fullerton.edu

## 📋 Project Information

- **Language:** Python 3.7+
- **Dependencies:** None (uses standard library only)
- **Description:** TCP client-server file transfer application with chunked transfers and progress bars

## 🚀 How to Execute

### 1. Start the Server

Open a terminal and run:

```bash
python server.py
```

The server will start listening on port 5001.

### 2. Start the Client

Open a **second terminal** and run:

```bash
python client.py
```

You'll see an interactive menu with the following options.

---

## 📝 Available Commands

```
1. Upload a file       - Upload a file from your local machine to the server
2. Download a file     - Download a file from the server to your local machine
3. List available files - View all files currently stored on the server
4. Exit                - Close the client application
```

### Example Usage

**Upload a file:**

```
Enter your choice (1-4): 1
Enter the path of file to upload: test_files/photo.jpg
```

**List available files:**

```
Enter your choice (1-4): 3
```

**Download a file:**

```
Enter your choice (1-4): 2
Enter the filename to download: photo.jpg
```

---

## 📁 Directory Structure

```
project/
├── server.py              # Server application
├── client.py              # Client application
├── README.md              # This file
├── server_files/          # Server storage (auto-created)
├── client_downloads/      # Downloaded files (auto-created)
└── test_files/            # Sample test files
```

---

## ⚙️ Configuration

**Server (server.py):**

- Host: `0.0.0.0` (listens on all interfaces)
- Port: `5001`
- Storage: `server_files/`
- Chunk size: `4096 bytes`

**Client (client.py):**

- Server: `127.0.0.1` (localhost)
- Port: `5001`
- Downloads: `client_downloads/`
- Chunk size: `4096 bytes`

---

## 🧪 Testing Multi-Client Support

To test multiple simultaneous connections:

1. Keep the server running
2. Open multiple terminals and run `python client.py` in each
3. Start uploads/downloads from each client

**Note:** Transfers with small files complete instantly. To see multiple active connections and progress bars in action, temporarily add delays to `server.py`:

```python
# Add after line 64 (inside upload loop):
time.sleep(1)

# Add after line 97 (inside download loop):
time.sleep(1)
```

Don't forget to remove these delays after testing!

---

## 📝 Protocol Details

**Upload:**

```
Client → Server: UPLOAD filename filesize\n
Server → Client: OK\n
Client → Server: [binary file data]
Server → Client: DONE\n
```

**Download:**

```
Client → Server: DOWNLOAD filename\n
Server → Client: OK filesize\n
Client → Server: READY\n
Server → Client: [binary file data]
Server → Client: DONE\n
```

**List Files:**

```
Client → Server: LIST\n
Server → Client: OK\n
Server → Client: filename1\n
Server → Client: filename2\n
...
Server → Client: DONE\n
```

---

## ✅ Features Implemented

- ✅ TCP client-server architecture
- ✅ Multi-client support (threading)
- ✅ Chunked file transfers (4KB chunks)
- ✅ Real-time progress bars
- ✅ Upload/Download functionality
- ✅ List available files
- ✅ Error handling (missing files, connection errors)
- ✅ Binary file support (images, PDFs, etc.)

---

## 🎯 Special Notes

- All file transfers use binary mode to preserve file integrity
- Server automatically creates storage directory if it doesn't exist
- Client automatically creates download directory if it doesn't exist
- Files with the same name will be overwritten on upload
- Progress bars show percentage and bytes transferred in real-time
