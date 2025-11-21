# Ping Manager (A+ Version)

## Overview

The **Ping Manager** performs high-concurrency ICMP tests from multiple network namespaces. Each namespace sends repeated `ping` requests to a target IP for a fixed duration. The module also runs a background health monitor to detect system stalls or Pi overloads.

Designed for: **Router stress testing**, **DHCP validation**, **multiclient connectivity**, and **real-time network health analysis**.

---

## Features

* Parallel ping execution across unlimited namespaces
* Configurable duration and target IP
* Micro-jitter between pings to avoid burst synchronization
* Integrated Raspberry Pi/host health monitoring using `health_worker`
* Clean async architecture using `asyncio`
* Behave BDD step definitions included

---

## Full Code

```python
import asyncio
import random
import time
from utils.pi_health_check import health_worker
from utils.logger import logger


async def run_cmd(cmd, suppress_output=False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(
            asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE
        ),
        stderr=(
            asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE
        ),
    )
    stdout, stderr = await proc.communicate()

    return {
        "returncode": proc.returncode,
        "stdout": None if suppress_output else stdout.decode(),
        "stderr": None if suppress_output else stderr.decode(),
    }


class PingManager:
    def __init__(self, target_ip, ping_duration):
        self.target_ip = target_ip
        self.duration = ping_duration

    async def worker(self, ns, end_time, results):
        success = True

        while time.time() < end_time:
            result = await run_cmd(
                f"sudo ip netns exec {ns} ping -c 1 -W 1 {self.target_ip}"
            )

            if result["returncode"] != 0:
                success = False
                logger.error(f"[FAIL] {ns} cannot reach {self.target_ip}")

            # jitter: prevents all namespaces pinging at exact same moment
            await asyncio.sleep(random.random() * 0.05)

        results[ns] = success

    async def run_test(self, namespaces):
        end_time = time.time() + self.duration
        results = {}

        stop_event = asyncio.Event()

        ping_tasks = [self.worker(ns, end_time, results) for ns in namespaces]

        # background health monitoring
        health_task = asyncio.create_task(health_worker(stop_event))

        await asyncio.gather(*ping_tasks)

        stop_event.set()
        await health_task

        return results
```

---

## Behave Step Definitions

```python
@when("all clients attempt to ping the router simultaneously")
def step_ping_clients(context):
    logger.info("------ PARALLEL CLIENT PING STARTED -----")

    ping_duration = context.config.get("ping_duration")

    pm = PingManager(context.router_ip, ping_duration)

    context.results = asyncio.run(
        pm.run_test([ns for ns in context.net_mgr.client_namespaces])
    )

    logger.info("----- STOPPED PING -----")


@when("all clients attempt to ping Google DNS")
def step_ping_google(context):
    logger.info("------ PARALLEL CLIENT PING TO GOOGLE DNS STARTED -----")

    google_dns_ip = "8.8.8.8"
    ping_duration = context.config.get("ping_duration")

    pm = PingManager(google_dns_ip, ping_duration)

    context.results = asyncio.run(
        pm.run_test([ns for ns in context.net_mgr.client_namespaces])
    )

    logger.info("----- STOPPED PING TO GOOGLE DNS -----")
```

---

## Notes

* Set `ping_duration` in your YAML config.
* All namespaces are fetched dynamically from your `NetworkManager` (`context.net_mgr`).
* Use this in combination with `download_manager`, `throughput_manager`, or multi-stage stress suites.

---

If you want an **A+ version for `tcp_manager.md`, `throughput_manager.md`**, or a **master README**, just ask!
