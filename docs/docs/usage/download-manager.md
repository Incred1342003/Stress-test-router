# Download Manager

_Handles high-load parallel downloads inside isolated Linux network namespaces while continuously monitoring Raspberry Pi system health._

---

## Overview

The **Download Manager** simulates large-scale download operations from multiple virtual network clients created using Linux network namespaces (`ip netns`).

### It performs:
- Parallel HTTP/HTTPS downloads  
- Per-namespace isolation  
- Time-bound transfers using `timeout`  
- Performance measurement (duration, interruptions)  
- Continuous 2-second interval Raspberry Pi health monitoring (CPU, RAM, Temp, Load)  
- Consolidated result reporting  

### Typical Use Cases:
- Stress-testing a router’s bandwidth distribution  
- Measuring network reliability under load  
- Running heavy download tests with 10–50+ virtual clients  
- Observing thermal and resource impact on Raspberry Pi during network pressure  

---

## Key Features

### Parallel Execution
Each namespace downloads the same file simultaneously.

### Timeout Protection
If a download takes longer than the configured limit, the OS kills the attempt.

### Resource Monitoring
A background task prints real-time Pi health:  
`CPU | Temp | RAM | Disk | Load`

### Accurate Performance Metrics
For each namespace:

| Metric       | Description                          |
|--------------|--------------------------------------|
| success      | Did download finish before timeout?  |
| duration     | Total time effort (seconds)          |
| interrupted  | True if download was force-killed    |
| stderr/stdout| Diagnostic information               |

---

## How It Works

### 1. `worker()`
Handles a **single client's download**:
- Executes `wget` inside the network namespace  
- Measures time taken  
- Stores result in dictionary  
- Logs success/failure  

### 2. `start_parallel_download()`
- Starts a health monitor task  
- Spawns download tasks for each namespace  
- Waits for all downloads  
- Stops health monitor  
- Returns structured output  

### 3. `health_worker()`
Runs asynchronously in the background to report Raspberry Pi performance every 2 seconds.

---

## Example Behave Step Usage

```python
@when("all clients start parallel download")
def step_download(context):
    url = context.config.get("test_download_url")
    timeout = context.config.get("download_timeout")

    dm = DownloadManager(url, timeout)

    context.results = asyncio.run(
        dm.start_parallel_download(context.net_mgr.client_namespaces)
    )
```
---
## Full Code — Download Manager
```bash
python
import asyncio
import time
from utils.logger import logger
from utils.pi_health_check import health_worker

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

class DownloadManager:
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

    async def worker(self, ns, results):
        cmd = (
            f"sudo ip netns exec {ns} "
            f"timeout {self.timeout} wget -q "
            f"-O /dev/null -o /dev/null "
            f"--no-cache {self.url}"
        )

        start = time.time()
        result = await run_cmd(cmd)

        duration = time.time() - start
        success = result["returncode"] == 0

        results[ns] = {
            "success": success,
            "duration": duration,
            "interrupted": not success,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }

        if success:
            logger.info(f"[OK] {ns} completed download in {duration:.2f} sec")
        else:
            logger.error(f"[FAIL] {ns} download failed after {duration:.2f} sec")

    async def start_parallel_download(self, namespaces):
        results = {}

        stop_event = asyncio.Event()
        tasks = [self.worker(ns, results) for ns in namespaces]

        health_task = asyncio.create_task(health_worker(stop_event))

        await asyncio.gather(*tasks)

        stop_event.set()
        await health_task

        return results
```

## Outputs Returned by DownloadManager
```bash
Example result structure:

json
{
  "ns1": {
    "success": true,
    "duration": 2.314,
    "interrupted": false,
    "stdout": "",
    "stderr": ""
  },
  "ns2": {
    "success": false,
    "duration": 5.000,
    "interrupted": true,
    "stdout": "",
    "stderr": "timeout expired"
  }
}
```

---

## Best Practices
- Use a fast mirror (e.g., Ubuntu ISO, sample files) for testing.

- Avoid extremely small files (results become unrealistic).

- Run high-load tests on Raspberry Pi 4 for accurate performance.

- Keep passive cooling or heatsinks attached.

- Avoid using Wi-Fi if testing router Ethernet performance.


