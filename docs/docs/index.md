# Router Stress Testing Automation

This project simulates **multiple virtual network clients** on a Raspberry Pi using:

- Linux Network Namespaces  
- macvlan interfaces  
- Parallel ping tests  
- Parallel file download tests  
- Live Raspberry Pi health monitoring  
- Automatic logging  
- Automated Behave (BDD) test execution  

The goal is to verify:

- Router stability under load  
- DHCP performance  
- Connectivity reliability  
- Packet loss  
- Stress handling during mass downloads  

---

## Features

- 🚀 Create 5/10/50+ virtual clients
- 📡 Simulate Wi-Fi or Ethernet clients
- 🔥 Run parallel pings & downloads
- 📊 Real-time Raspberry Pi health (CPU, Temp, RAM, Disk, Load)
- 🧪 Behave-based test scenarios
- 📝 Structured logs per test
- 📦 Easy to extend

---

## Quick Start

```bash
mkdocs serve
```