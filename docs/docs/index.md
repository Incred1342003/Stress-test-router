# Stress Test Router Documentation

## Overview

This project provides a comprehensive automation framework to test router performance under load using Raspberry Pi as the controller. It simulates multiple virtual network clients, performs parallel pings, executes simultaneous downloads, and monitors Raspberry Pi health metrics — all in real time.

## What This Project Does

* Creates **virtual network clients** using Linux network namespaces.
* Simulates **parallel ping tests** to measure connectivity.
* Runs **simultaneous download tests** to stress-test bandwidth and routing.
* Monitors Raspberry Pi's **CPU, RAM, Disk, Temperature, and Load** every 2 seconds.
* Logs everything with a clean, structured format for analysis.
* Allows integrating tests through **Behave (BDD)**.

## Why This Project

Routers often behave differently under high client load. By creating multiple isolated namespaces, you simulate dozens of clients without real hardware. This is useful for:

* Network load testing
* Router firmware testing
* Performance benchmarking
* Automated QA for network devices

## Technologies Used

### **Programming & Frameworks**

* **Python 3** (asyncio-based parallel execution)
* **Behave (Gherkin)** for BDD test scenarios
* **Linux Network Namespace** for the virtual client creation
* **MkDocs + Material Theme** for documentation

### **Linux Networking Tools**

* `ip netns`, `macvlan`, `veth` for virtual clients
* `ping`, `wget` for network operations

### **Hardware Requirement**

* **Raspberry Pi 4/3** running Raspberry Pi OS
* Stable Internet Connection
* Router
* SSH Access Recommended [Not neccessary]

---

## Raspberry Pi Setup Requirements

Before running tests, ensure your Raspberry Pi meets the following:

### 1. **Install Required Packages**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv net-tools iputils-ping wget -y
```

### 2. **Install Python Dependencies**

```bash
pip3 install psutil behave mkdocs mkdocs-material
```

After running tests, namespaces will appear here.

### 3. Project Folder Structure

```
Stress-test-router/
│
├── src/
│   ├── ping_manager.py
│   ├── download_manager.py
│   ├── health_monitor.py
│   └── ...
│
├── utils/
│   └── logger.py
│
├── features/
│   ├── steps/
│   └── test files...
│
├── docs/
│   └── mkdocs documentation
│
└── config.yaml
```

---

## What Happens When You Run the Project

Below is the complete execution flow:

### **1. Namespace Creation**

The system creates `N` virtual clients using macvlan:

```bash
sudo ip netns add client1
sudo ip link add link eth0 client1-macvlan type macvlan mode bridge
sudo ip link set client1-macvlan netns client1
```

Each namespace becomes an isolated client.

### **2. Ping Test Execution**

Each client pings a target IP (e.g., 8.8.8.8) for X seconds:

```
client1 → ping 8.8.8.8
client2 → ping 8.8.8.8
...
```

All run in parallel using **asyncio**.

### **3. Download Test Execution**

Each namespace downloads the same file simultaneously using `wget`. This stresses:

* LAN ↔ Router performance
* Firewall/NAT table efficiency
* Bandwidth distribution

### **4. Real-Time Raspberry Pi Monitoring**

Every 2 seconds the Pi reports:

* CPU Utilization
* Temperature (if sensor available)
* RAM Usage
* Disk Usage
* System Load

Example log:

```
[PI HEALTH] CPU=34% | Temp=52.1C | RAM=48% | Disk=12% | Load=0.98
```

### **5. Final Results**

After the test stops, Behave prints organized reports:

* Successful/failed clients
* Download duration
* Ping success
* Router response consistency

---

## Requirements to Run Everything

### **Hardware**

* Raspberry Pi 4/3 with 2GB+ RAM recommended
* SD Card 16GB+

### **Software**

* Python 3.9+
* Linux with network namespace support
* Behave
* MkDocs / MkDocs Material

### **Network Requirements**

* Router connected via Ethernet (preferred)
* Internet access for ping/google tests
* Download URL accessible

---

## Summary

This project provides:

* Fully automated router stress testing
* Real-time health monitoring
* Raspberry-Pi-driven load simulation
* Professional documentation with MkDocs

You now have a full overview of the entire system. Next pages will go deeper into setup, usage, and internals.
