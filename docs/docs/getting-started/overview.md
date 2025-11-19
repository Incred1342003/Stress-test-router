# Project Overview

This automation framework stress-tests any router by creating virtual clients and executing heavy network operations from each.

### Why?
Physical devices are expensive and slow to set up.  
Linux namespaces allow you to create **hundreds of clients instantly**.

---

## What the System Does

### 1. Creates virtual clients
Each client has:
- Unique IP  
- Unique MAC  
- Isolated namespace  
- macvlan interface

### 2. Performs tests
- **Ping Tests** – Google DNS or Router  
- **Download Tests** – Parallel 20 MB downloads  
- **Health Monitoring** – Every 2 sec during tests  

### 3. Records results
Stored in logs under: `network_stress_report.log`

### 4. Used Technologies

| Component | Purpose |
|----------|---------|
| Python | Management scripts |
| Behave | Test automation |
| Linux netns | Virtual clients |
| macvlan | Interface cloning |
| psutil | Health monitoring |
| wget | Download benchmarking |
| ping | Connectivity tests |
| MkDocs | Documentation |