import asyncio
import random
import time
import psutil
import os
import paramiko
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


async def get_router_health(host, username, password, stop_event):
    while not stop_event.is_set():
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password, timeout=10)

            # Run all commands in one exec so Dropbear doesn't close the channel
            commands = "top -bn1 | head -5; cat /proc/loadavg; free -m; df -h /"
            stdin, stdout, stderr = ssh.exec_command(commands)
            output = stdout.read().decode().strip()
            ssh.close()

            # Split into lines and ignore banners
            lines = [
                line for line in output.splitlines()
                if not ("Connected" in line or "Authentication" in line)
            ]

            cpu_usr = cpu_sys = cpu_idle = "N/A"
            mem_used = mem_free = "N/A"
            load1 = "N/A"
            disk_root = "N/A"

            for line in lines:
                if line.startswith("CPU:"):
                    parts = line.split()
                    try:
                        cpu_usr = parts[1].replace("%", "")
                        cpu_sys = parts[3].replace("%", "")
                        cpu_idle = parts[7].replace("%", "")
                    except Exception:
                        pass
                elif line.startswith("Mem:"):
                    parts = line.split()
                    try:
                        mem_used = parts[1].replace("K", "")
                        mem_free = parts[3].replace("K", "")
                    except Exception:
                        pass
                elif line.startswith("Load average:"):
                    try:
                        load1 = line.split()[2]
                    except Exception:
                        pass
                elif line.startswith("/"):
                    try:
                        disk_root = line.split()[4].replace("%", "")
                    except Exception:
                        pass

            logger.info(
                f"[ROUTER HEALTH] CPU usr={cpu_usr}% sys={cpu_sys}% idle={cpu_idle}% | "
                f"Mem used={mem_used}K free={mem_free}K | Disk={disk_root}% | Load={load1}"
            )

        except Exception as e:
            logger.error(f"[ROUTER HEALTH] Error: {e}")

        await asyncio.sleep(5)


class PingManager:
    def __init__(self, target_ip, ping_duration, ip_version):
        self.target_ip = target_ip
        self.duration = ping_duration
        self.ip_version = ip_version

    async def worker(self, ns, end_time, results):
        success = True
        while time.time() < end_time:
            ping_cmd = "-6" if self.ip_version == "IPV6" else "-4"
            result = await run_cmd(
                f"sudo ip netns exec {ns} ping {ping_cmd} -c 1 -W 1 {self.target_ip}"
            )
            if result["returncode"] != 0:
                success = False
                logger.error(f"[FAIL] {ns} cannot reach {self.target_ip}")
            await asyncio.sleep(random.random() * 0.05)
        results[ns] = success

    async def run_test(self, namespaces):
        end_time = time.time() + self.duration
        results = {}

        stop_event_pi = asyncio.Event()
        stop_event_router = asyncio.Event()

        ping_tasks = [self.worker(ns, end_time, results) for ns in namespaces]

        pi_task = asyncio.create_task(health_worker(stop_event_pi))
        router_task = asyncio.create_task(
            get_router_health("192.168.1.1", "operator", "Charter123", stop_event_router)
        )

        await asyncio.gather(*ping_tasks)

        stop_event_pi.set()
        stop_event_router.set()

        await pi_task
        await router_task

        return results

