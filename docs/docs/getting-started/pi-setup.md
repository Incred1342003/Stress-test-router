# Raspberry Pi Setup Guide

This guide explains how to correctly prepare a **Raspberry Pi** for running the *Stress‑Test‑Router* project.  
Follow each step carefully to ensure stable network simulation, macvlan creation, and health monitoring during stress tests.

---

# Supported Raspberry Pi Models

The project has been tested and works perfectly on:

- **Raspberry Pi 3B+**
- **Raspberry Pi 4 (4GB/8GB)**
- **Raspberry Pi Zero 2W**
- **Raspberry Pi CM4**

Any Pi running **Raspberry Pi OS (32‑bit or 64‑bit)** is supported.

---

# 1. Update and Upgrade the System

Before installing anything, update your Pi:

```bash
sudo apt update && sudo apt upgrade -y
```

---

# 2. Install Required System Packages

These tools are required for networking, namespaces, and monitoring.

```bash
sudo apt install -y python3 python3-pip iproute2 net-tools git wget                     dnsutils htop nmap
```

---

# 3. Install Python Dependencies

Install required Python packages globally or with `--user`.

```bash
sudo pip3 install behave mkdocs mkdocs-material psutil
```

(If you cloned the project, dependencies will also come from `requirements.txt`.)

---

# 4. Test Basic Network Commands

Ensure Pi supports ping and DNS resolution:

```bash
ping -c 3 google.com
dig google.com
```

---

# 5. Recommended Monitoring Tools

Although the project prints system health during tests, these tools help during debugging:

```bash
sudo apt install -y sysstat btop iotop vnstat
```

Run:

```bash
top
btop
vnstat
```

---

🎉You are all set now got to [Installation Process.](../getting-started/installation.md)

