# Network Namespace Management

This document explains how network namespaces are created, configured, and used in this project to simulate multiple isolated clients on a Raspberry Pi.

It includes:

* Concept overview
* CLI commands for manual namespace creation
* Full implementation code for the `NetworkManager` class
* Usage patterns inside Behave feature tests

---

## What Are Network Namespaces?

Linux **network namespaces** allow isolation of networking stacks. Each namespace has its own:

* Interfaces
* Routing tables
* IP addresses
* DNS resolver config

In this project, namespaces simulate **multiple independent clients**, each with its own MAC, IP, and routing — perfect for router stress testing.

---

## How We Create Clients

We use the following strategy:

* Create a namespace: `ns1`, `ns2`, ...
* Create a `macvlan` interface inside each namespace
* Assign unique MAC addresses
* Request IP from router using `dhclient`
* Add DNS resolvers

---

## Manual Commands (For Understanding)

Below are the raw Linux commands the code automates.

### Create a namespace:

```bash
sudo ip netns add ns1
```

### Create a macvlan linked to the parent interface:

```bash
sudo ip link add link eth0 macvlan1 type macvlan mode bridge
```

### Move the macvlan into namespace:

```bash
sudo ip link set macvlan1 netns ns1
```

### Bring interfaces up:

```bash
sudo ip netns exec ns1 ip link set dev macvlan1 up
sudo ip netns exec ns1 ip link set lo up
```

### Request IP from router:

```bash
sudo ip netns exec ns1 dhclient -v macvlan1 \
    -pf /run/dhclient-ns1.pid \
    -lf /var/lib/dhcp/dhclient-ns1.leases
```

### Ping from the namespace:

```bash
sudo ip netns exec ns1 ping -c 1 8.8.8.8
```

### Delete namespace:

```bash
sudo ip netns delete ns1
```

---

## Full NetworkManager Code

Below is the full implementation used in this project.

```python
<CODE_PLACEHOLDER>
```

---

## Namespace Cleanup Logic

If any namespace fails to get an IP, the system:

* Releases DHCP leases
* Deletes macvlan interfaces
* Deletes namespace folders
* Resets all state

Ensures **clean environment** for every test run.

---

## How It’s Used Inside Behave

Example:

```gherkin
Given I create 10 virtual clients using macvlan
When all clients attempt to ping Google DNS
Then all clients should respond successfully
```

The step file calls:

```python
context.net_mgr.create_clients(10)
```

---

## Notes

* Each namespace gets a unique MAC address.
* DNS is injected using `/etc/netns/<ns>/resolv.conf`.
* All commands run in async for parallel creation.

---

Add your full code below where `<CODE_PLACEHOLDER>` is.
