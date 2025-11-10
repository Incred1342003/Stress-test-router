# ⚡ Stress Test Router

This project is designed to **stress test routers** by simulating multiple client connections and measuring system performance such as CPU utilization and response stability.

---

## 🚀 Installation Guide

Follow the steps below to set up and run the project on your **Raspberry Pi**.

### 1. Clone the Repository
```bash
git clone https://github.com/panditpankaj21/Stress-test-router.git
cd Stress-test-router
```
### 2. Install Dependencies
Ensure Python is installed, then run:

```bash
pip install -r requirements.txt
```
### 3. Configure Network Settings
- Set your network interface (e.g., eth0, wlan0)
- Set your router IP address as required by your setup or inside the configuration section

### 4. Run the Test
Execute the following command to start the stress test:

```bash
sudo behave
```
### ⚙️ Notes
- Run the command with `sudo` to ensure full network access permissions.
- Make sure your Raspberry Pi is connected to the target router before running the test.
