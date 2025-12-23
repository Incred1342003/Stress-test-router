import asyncio
import random
import time

from prettytable import PrettyTable
from utils.logger import logger
from utils.pi_health_check import health_worker


async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "returncode": proc.returncode,
        "stdout": stdout.decode().strip() if stdout else "",
        "stderr": stderr.decode().strip() if stderr else "",
    }


async def get_router_health(router_ssh, host, username, password, stop_event):
    while not stop_event.is_set():
        router_ssh.get_health()
        await asyncio.sleep(5)


class PingManager:
    def __init__(self, router_ssh, target_ip, ping_duration, ip_version):
        self.router_ssh = router_ssh
        self.target_ip = target_ip
        self.duration = ping_duration
        self.ip_version = ip_version

    async def worker(self, ns, end_time, results):
        success = True
        received_pings = 0
        start_time = time.time()
        ping_cmd = "-6" if self.ip_version == "IPV6" else "-4"

        while time.time() < end_time:
            result = await run_cmd(
                f"sudo ip netns exec {ns} ping {ping_cmd} -c 1 -W 1 {self.target_ip}"
            )
            if result["returncode"] == 0:
                received_pings += 1
            else:
                success = False
                logger.error(f"[FAIL] {ns} cannot reach {self.target_ip}")
            await asyncio.sleep(random.random() * 0.05)

        actual_duration = time.time() - start_time

        total_bytes = received_pings * 128
        speed_mbps = (total_bytes * 8) / (actual_duration * 1024 * 1024)

        results[ns] = {
            "success": success,
            "speed": round(speed_mbps, 6),
            "duration": round(actual_duration, 2),
            "error": "" if success else "Packet Loss",
        }

    def display_results(self, results):
        table = PrettyTable()
        table.field_names = [
            "Namespace",
            "Status",
            "Time (s)",
            "Speed (Mbps)",
            "Remarks",
        ]
        table.align["Namespace"] = "l"
        table.align["Status"] = "c"
        table.align["Remarks"] = "l"

        success_count = 0
        for ns, data in sorted(results.items()):
            status = "OK" if data["success"] else "FAIL"
            if data["success"]:
                success_count += 1
            table.add_row([ns, status, data["duration"], data["speed"], data["error"]])

        logger.info(
            "\n"
            + "═" * 70
            + "\n"
            + f"PING SUMMARY | SUCCESS: {success_count}/{len(results)}"
            + "\n"
            + "═" * 70
        )
        logger.info(f"\n {table}\n" + "═" * 70 + "\n")

    async def run_test(self, namespaces):
        end_time = time.time() + self.duration
        results = {}
        stop_event_pi = asyncio.Event()
        stop_event_router = asyncio.Event()

        tasks = [self.worker(ns, end_time, results) for ns in namespaces]

        pi_task = asyncio.create_task(health_worker(stop_event_pi))
        router_task = asyncio.create_task(
            get_router_health(
                self.router_ssh,
                "192.168.1.1",
                "operator",
                "Charter123",
                stop_event_router,
            )
        )

        await asyncio.gather(*tasks)

        stop_event_pi.set()
        stop_event_router.set()
        await pi_task
        await router_task

        self.display_results(results)
        return results
