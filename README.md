## Stress-Test Router: High-Performance Router Stress-Testing Framework

Stress-Test Router is a tool for evaluating router performance by simulating numerous virtual clients using **Linux network namespaces** and **macvlan** technology, powered by an **async workload** on a **Raspberry Pi** with integrated health monitoring.

<p align="center"> <img src="https://img.shields.io/badge/CI-Passing-brightgreen?style=flat-square" /> <img src="https://img.shields.io/badge/Docs-Available-blue?style=flat-square" /> <img src="https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square" /> <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=flat-square" /> <img src="https://img.shields.io/github/license/panditpankaj21/Stress-test-router?style=flat-square" /> </p>

## Full Documentation

[Read Documentation](https://panditpankaj21.github.io/Stress-test-router/)

## Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [Architecture](#-architecture)
* [Requirements](#-requirements)
* [Installation](#-installation)
* [Configuration](#-configuration)
* [Running Tests](#-running-tests)
* [Project Structure](#-project-structure)
* [Contributing](#-contributing)
* [License](#-license)


## Overview

**Stress-Test Router** is a tool designed to evaluate router performance by simulating **multiple virtual clients** using Linux network namespaces.

It measures:

* **DHCP behavior**
* **IP assignment stability**
* **Download performance**
* **Ping latency**
* **Raspberry Pi CPU, RAM, Temp & Load** during stress

This tool is useful for:

* **Router testing labs**
* **IoT/home network experiments**
* **Raspberry Pi network benchmarking**
* **Automated network performance testing**

## Key Features

### Network Namespace Simulation

* Automatically creates **N isolated clients** using **macvlan**.
* Each client gets its own **network stack, IP, routing table, and DNS**.

### DHCP & Router Validation

* Ensures each namespace receives **IP dynamically**.
* Validates router’s **DHCP performance** under load.

### Parallel Tasks

* **Concurrent ping tests**
* **Concurrent download tests**
* Fully **asynchronous** and optimized

### Live Raspberry Pi Health Monitoring

During ping/download tests, the system logs:

* **CPU usage**
* **Temperature**
* **Memory usage**
* **Disk usage**
* **Load average**

### Detailed Logging

* Structured logs per namespace
* Fail/success reporting
* Duration measurement for each worker

### Automated via Behave (BDD)

* Clear scenario definitions
* Easy to expand new test cases
* CI supported

## Requirements

### Hardware

* **Raspberry Pi** (3B+, 4, Zero 2W)
* **Router** under test
* **Ethernet** recommended (Wi-Fi also works)

### Software

* **Python 3.10+**
* **Linux OS** (Raspberry Pi OS recommended)
* **iproute2, dhclient, wget**

---

## Installation

Clone the repository and install dependencies:

```bash
git clone [https://github.com/panditpankaj21/Stress-test-router.git](https://github.com/panditpankaj21/Stress-test-router.git)
cd Stress-test-router
pip install -r requirements.txt
```

## Configuration

All configuration is managed in: **`config.yaml`**

Configure the following settings:

| Setting | Description |
| :--- | :--- |
| **interface** | Network interface (eth0, wlan0, etc.) |
| **router\_ip** | Router default gateway IP |
| **ping\_duration** | Parallel ping test duration |
| **download\_timeout** | Max download time |
| **client\_count** | Number of namespaces (virtual clients) |
| **Export to Sheets** | *(This line appears to be an instruction, not a setting)* |

**Example:**

```yaml
interface: "eth0"
router_ip: "192.168.1.1"
ping_duration: 30
download_timeout: 60
client_count: 20
```


## Running Tests

**`sudo` is required** for namespace/macvlan operations.

* **Run all tests:**
    ```bash
    sudo behave
    ```
* **Run a specific feature:**
    ```bash
    sudo behave features/ping.feature
    ```
* **Run tests by tag:**
    ```bash
    sudo behave --tags "@download"
    ```

## Contributing

Please follow these steps:

1.  **Fork** the repo
2.  Create a new **branch**
3.  **Commit** changes
4.  Submit a **Pull Request**

**CI checks must pass before merge.**

## 📄 License

This project is licensed under the **MIT License**.