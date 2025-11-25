# File Transfer Application - Phase 2: AWS Deployment

## 👥 Team Members

- Andrew Chang - ankechang2752@csu.fullerton.edu
- Hyndavi Teegela - Hyndavi.teegela@csu.fullerton.edu
- Jenny Phan - Jphan131@csu.fullerton.edu
- Jason Luu - jluu6324@csu.fullerton.edu
- Sibi Ukeshkumar - sibi@csu.fullerton.edu

## 📋 Project Information

- **Language:** Python 3.7+
- **Dependencies:** None (uses standard library only)
- **Description:** Multi-client FTP server on AWS EC2 with two-connection architecture

## 🚀 Quick Start

### Deploy Server to EC2

```bash
# 1. SSH into EC2
ssh -i file-transfer-key.pem ubuntu@3.138.32.213

# 2. Upload server code
scp -i file-transfer-key.pem server.py ubuntu@3.138.32.213:~/

# 3. Run server
python3 server.py
```

### Run Client Locally

```bash
# 1. Update SERVER_HOST in client.py
SERVER_HOST = "3.138.32.213"

# 2. Run client
python client.py
```

---

## 📝 Commands

| Command  | Description               | Usage                      |
| -------- | ------------------------- | -------------------------- |
| Upload   | Upload file to server     | Option 1 → Enter file path |
| Download | Download file from server | Option 2 → Enter filename  |
| List     | Show available files      | Option 3                   |
| Exit     | Close connection          | Option 4                   |

---

## ⚙️ Configuration

**EC2 Server:**

- Public IP: `3.138.32.213`
- Control Port: `5001`
- Data Port: `5002`

**Security Group:**

- Port 5001: TCP from 0.0.0.0/0
- Port 5002: TCP from 0.0.0.0/0
- Port 22: SSH access

---

## 🧪 Testing

**Multi-Client Test Results:**

- ✅ Concurrent uploads (2 clients)
- ✅ Concurrent downloads (2 clients)
- ✅ List files command
- ✅ Mixed operations (3 clients)

See `REPORT.md` for detailed testing evidence and logs.

---

## 🔧 Troubleshooting

**Connection Refused:**

- Check server is running: `ps aux | grep server.py`
- Verify security group ports 5001 & 5002 are open
- Confirm EC2 instance is running

**Timeout Errors:**

- Test connectivity: `telnet 3.138.32.213 5001`
- Check firewall rules
- Verify correct public IP

**Server Stops When SSH Closes:**

```bash
# Run in background
nohup python3 server.py > server.log 2>&1 &
```

---

## 📁 Project Structure

```
project/
├── server.py           # Server (runs on EC2)
├── client.py           # Client (runs locally)
├── README.md           # This file
├── REPORT.md           # Technical documentation
├── screenshots/        # Testing evidence
└── test_files/         # Sample files
```

---

## ✅ Requirements Met

| Requirement      | Status                     |
| ---------------- | -------------------------- |
| Protocol design  | ✅ Two-connection FTP-like |
| GET (Download)   | ✅ Tested                  |
| PUT (Upload)     | ✅ Tested                  |
| LS (List)        | ✅ Tested                  |
| Multi-client     | ✅ Threading               |
| Cloud deployment | ✅ EC2                     |
| Documentation    | ✅ README + REPORT         |

---

## 📄 Additional Documentation

- **REPORT.md** - Complete technical details, architecture, testing analysis
- **Screenshots/** - EC2 console, security groups, testing evidence

---

## 📞 Support

For questions, contact any team member listed above.
