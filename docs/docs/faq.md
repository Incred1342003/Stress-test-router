# Frequently Asked Questions (FAQ)

This FAQ covers all common questions developers face while using the **Stress-Test-Router** automation suite.  
If you are stuck, start here.

* * *

## 1. What does this project actually do?

This system creates **multiple virtual clients** using Linux network namespaces + macvlan and performs:

-   Parallel ping tests
    
-   Parallel download tests
    
-   Router stress testing
    
-   Real-time Raspberry Pi health monitoring
    

It simulates _real world network load_ on a router.

## 2. Does this work on Windows?

**No.**  
Windows does **not** support macvlan or Linux namespaces.

✔ Works on:

-   Raspberry Pi (Recommended)
    
-   Ubuntu / Debian Linux
    
-   Any native Linux machine
    
-   VirtualBox Ubuntu VM (with bridged adapter)
    

Does not work on:

-   Windows
    
-   WSL
    
-   Docker Desktop (Macvlan restricted)

## 3. Why do some clients not get an IP address?

Possible reasons:

-   Router DHCP service is overloaded
    
-   Router DHCP pool is exhausted
    
-   Wrong interface configured
    
-   Slow DHCP response
    
-   Network interference
    
-   macvlan mode restrictions
    

See **Troubleshooting → “Clients Not Receiving IP”**.

## 4\. How many clients can I realistically create?

It depends on:

| Device | Recommended Max Namespaces |
| --- | --- |
| Raspberry Pi Zero 2W | 10–15 |
| Raspberry Pi 3B+ | 25–40 |
| Raspberry Pi 4 (2GB/4GB) | 40–75 |
| Ubuntu PC | 100+ |

More clients → more CPU usage because each namespace runs dhclient, ping, wget, etc.

## 5. Is it safe to run on my router?

Yes, the test is designed to be **non-destructive**.  
But note:

-   Parallel downloads may consume bandwidth
    
-   Router CPU may temporarily spike
    
-   Weak routers may reboot under heavy load
    

It does **NOT**:

-   Change router configuration
    
-   Attack the router
    
-   Modify firmware

## 6. Why do downloads fail randomly?

Most common reasons:

-   Router is overloaded
    
-   DNS not set inside namespace
    
-   URL server throttles requests
    
-   Timeout too small
    

Fix DNS:

`echo -e "nameserver 8.8.8.8\nnameserver 1.1.1.1" | sudo tee /etc/netns/nsX/resolv.conf`

## 7. Why does `mkdocs serve` not reload live?

On Windows, MkDocs has issues with:

-   OneDrive synced folders
    
-   VS Code auto-save delay
    
-   File locking problems
    

Fix: Move project out of OneDrive.

## 8. Why does `behave` skip scenarios?

If namespace creation fails, we **intentionally skip** the scenario to avoid corrupt state.

Check logs:

`Skipping scenario due to failed client creation`

Fix in **Network Troubleshooting**.

## 9\. Where are the logs stored?

Logs are printed to console and also saved in:

`/logs/stress_test.log`

(if you enabled file logging in your logger settings)

## 10. Why does Pi health monitoring freeze?

Monitor slows down when:

-   Too many namespaces are running
    
-   CPU hits 80%+
    
-   Temperature >80°C
    
-   `vcgencmd` is missing
    

Install:

`sudo apt install -y libraspberrypi-bin`

## 11. Why am I getting “permission denied”?

Use sudo:

`sudo behave sudo python3 main.py`

Linux namespaces require elevated privileges.

## 12. Can I test wireless clients?

Not with macvlan.  
macvlan works only on **Ethernet** interface.

For Wi-Fi simulation:

-   Use **mac80211\_hwsim**
    
-   Or multiple USB Wi-Fi dongles
    

## **13\. Can I export documentation as PDF?**

# 

MkDocs Material supports it. Run:

`pip install mkdocs-with-pdf`

Then run:

`mkdocs build`

A `site/pdf/` directory will be created.

## 14. Can I add more test modules?

Absolutely.

This project is modular.  
Create new Python classes inside `utils/` or `managers/`.

Example:

`managers/   speedtest_manager.py   authentication_manager.py   packetloss_manager.py`


## 15. Why does WSL not support macvlan?

Because WSL2 runs on a virtual NIC and does not allow:

-   Promiscuous mode
    
-   Bridging
    
-   Macvlan creation
    

Use native Linux or Pi.

## 16. Does the project need root access?


Yes — **namespace**, **macvlan**, and **dhclient** all require root.

## 17. Can this damage the router?

No, but:

-   Very weak routers may reboot under load
    
-   It may saturate bandwidth temporarily
    

This is normal for stress testing.

## 18. Can this be used for enterprise routers?

Yes.  
It works with:

-   MikroTik
    
-   TP-Link
    
-   Netgear
    
-   D-Link
    
-   ASUS
    
-   Cisco home-grade routers
    
-   Ubiquiti (with DHCP enabled)
    

This is a **DHCP + ICMP + download stress tester** — works with any DHCP-enabled router.