# Troubleshooting Guide

This page provides solutions for common problems encountered while running the **Stress-Test-Router** automation suite on Raspberry Pi or Linux systems.  
If something breaks, this is the first place to check.

## 1. Clients Not Receiving IP Address

### Symptoms

-   Namespace creation succeeds, but no IP is assigned.
    
-   Logs show:
    
    `did not get IP within X seconds`
    
-   Scenario is aborted due to failed namespace creation.
    

### Possible Causes & Fixes

#### 1. DHCP Server on Router Not Responding

Make sure your router is:
-   Powered on
-   Not overloaded
-   Has DHCP enabled
    

Fix:
Reboot the router and try again:

`sudo systemctl restart dhcpcd`


#### 2. Physical Interface Name Incorrect

Check your Pi’s interface name:

`ip link`

Typical values:
-   `eth0`
-   `wlan0`
    
Make sure your `config.yaml` uses the correct interface:

`interface: eth0`

#### 3. DHCP Client Not Installed

Install it:

`sudo apt install -y isc-dhcp-client`

## 2. Wget Downloads Failing

### Symptoms

-   Download manager reports:
    `[FAIL] nsX download failed`
    

### Causes & Fixes

#### 1. Router Has No Internet

Test from host:

`ping 8.8.8.8`

#### 2. DNS Failing

Fix by rewriting resolver file for all namespaces:

`echo -e "nameserver 8.8.8.8\nnameserver 1.1.1.1" | sudo tee /etc/resolv.conf`

## 3. Pings Failing Inside Namespace

### Symptoms

-   Clients cannot ping router or 8.8.8.8
    
-   Behavior inconsistent
    

### Fixes

#### 1. Enable IP Forwarding

`sudo sysctl -w net.ipv4.ip_forward=1`

#### 2. Flush iptables

`sudo iptables -F sudo iptables -t nat -F`

#### 3. Check namespace interface state

`sudo ip netns exec ns1 ip link show`

Interface must be **UP**.

## 4. mkdocs Serve Not Live Updating

### Symptoms

-   Markdown changes not reflected
-   `mkdocs serve` only updates on restart

### Fix

#### 1. Ensure you’re running from the root mkdocs directory

Correct:
`Stress-test-router/docs/`

Run:
`mkdocs serve`

#### 2. Disable OneDrive Sync Conflicts (Windows)

Move your project out of OneDrive:

`C:\Projects\Stress-test-router`

MkDocs often fails to watch files inside OneDrive.

## 5. Behave Scenarios Not Detected

### Symptoms

-   Steps not running
-   Behave says:
    `Step not found`
    

### Fix

Check folder structure:

`features/steps/*.py`

Make sure your step function names match your `.feature` files.


## 6. CPU/Temperature Monitoring Not Working

### Symptoms

-   `vcgencmd` not found
-   Health monitor throws warnings
    

### Fix

Install Pi utilities:

`sudo apt install -y libraspberrypi-bin`

To test:

`vcgencmd measure_temp`

## 7. Permission Denied Errors

### Symptoms

-   Namespace creation fails
-   dhclient fails
-   ping fails inside namespace
    

### Fix

Run with **sudo**:

`sudo behave`

or:

`sudo python3 main.py`

## 8. WSL Users: Macvlan Will Not Work

### Symptoms

-   `ip link add macvlan...` fails
-   Pings fail
    

### Reason

WSL does **not** support macvlan.

### Fix:

Run on:
-   Raspberry Pi
-   Linux Machine
    
-   VirtualBox + Ubuntu with bridged adapter
    

WSL is not supported.


## 9. Router Blocks ICMP or Wget Traffic

### Symptoms

-   Pings work from host but not from namespace
-   Download test fails
    

### Fixes:

-   Disable firewall in router
-   Disable parental control
-   Disable guest network isolation


## 10. Cleanup Failing / Zombie Namespaces

### Fix

Run:

`sudo ip -all netns delete sudo rm -rf /etc/netns/*`