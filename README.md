## Stress-Test Router

Stress-Test Router is a tool for evaluating router performance by simulating numerous virtual clients using **Linux network namespaces** and **macvlan** technology, powered by an **async workload** on a **Raspberry Pi** with integrated health monitoring.

<p > 
    <a href="https://behave.readthedocs.io/en/stable/">
        <img 
            src="https://img.shields.io/badge/Behave-BDD%20Framework-green?style=flat-square" 
            alt="Behave"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://kernel.org/doc/html/latest/">
        <img 
            src="https://img.shields.io/badge/Linux-Kernel%20Docs-black?style=flat-square" 
            alt="Linux"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://man7.org/linux/man-pages/man7/network_namespaces.7.html">
        <img 
            src="https://img.shields.io/badge/Network%20Namespace-Isolation%20Tech-blue?style=flat-square" 
            alt="Linux Network Namespace"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://github.com/panditpankaj21/Stress-test-router/actions">
        <img 
            src="https://img.shields.io/badge/CI-Passing-brightgreen?style=flat-square" 
            alt="CI Status"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://github.com/panditpankaj21/Stress-test-router/tree/main/docs">
        <img 
            src="https://img.shields.io/badge/Docs-Available-blue?style=flat-square" 
            alt="Documentation"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://www.python.org/downloads/release/python-3100/">
        <img 
            src="https://img.shields.io/badge/Python-3.10%2B-yellow?style=flat-square" 
            alt="Python Version"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://www.raspberrypi.com/software/">
        <img 
            src="https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=flat-square" 
            alt="Platform"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
    <a href="https://github.com/panditpankaj21/Stress-test-router/blob/main/LICENSE">
        <img 
            src="https://img.shields.io/github/license/panditpankaj21/Stress-test-router?style=flat-square" 
            alt="License"
            style="max-width: 100%; border-radius:3px"
        />
    </a>
</p>


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

## Quick Setup

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