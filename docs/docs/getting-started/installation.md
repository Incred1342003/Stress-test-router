# Installation Guide

This Section explains how to install, configure, and prepare the **Stress-Test-Router** project on any Linux system or Raspberry Pi device.

---

# Project Installation

## 1. Clone the Repository
```bash
git clone https://github.com/panditpankaj21/Stress-test-router.git
cd Stress-test-router
```

---

## 2. Install Python Dependencies
Make sure Python **3.9+** is installed.

```bash
pip install -r requirements.txt
```

If you are on Raspberry Pi and need system-level privileges:

```bash
sudo pip3 install -r requirements.txt
```

---

## 3. Install System Packages (Linux / Raspberry Pi)
The project uses tools like `ip`, `iproute2`, `macvlan`, and networking utilities.

```bash
sudo apt update
sudo apt install -y python3 python3-pip iproute2 net-tools git wget
```

Additional recommended packages:

```bash
sudo apt install -y dnsutils htop nmap
```

---

## 4. Run Tests Using Behave (BDD Framework)

### Run **ALL** feature tests:
```bash
sudo behave
```

### Run a **specific** feature:
```bash
sudo behave features/<feature_name>.feature
```

### Run by **tag**:
```bash
sudo behave --tags="@tag_name"
```

---

# Documentation Setup (MkDocs)

The project includes a full documentation system using **MkDocs + Material Theme**.

### Enter docs directory:
```bash
cd docs
```

### Start live preview:
```bash
mkdocs serve
```

Documentation is available at:
```
http://127.0.0.1:8000
```

### Build documentation:
```bash
mkdocs build
```

### Show help:
```bash
mkdocs -h
```

---

# 🎉 Installation Complete!

You are now ready to run network stress tests and explore full documentation.
