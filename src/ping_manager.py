import asyncio
import random
import time
from utils.logger import logger

class PingManager:
    def __init__(self, router_ip="192.168.1.1", duration=60):
        self.router_ip = router_ip
        self.duration = duration

    async def run_cmd(self, cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        await proc.communicate()

    async def worker(self, ns, end_time):
        while time.time() < end_time:
            await self.run_cmd(
                f"sudo ip netns exec {ns} ping -c 1 8.8.8.8"
            )
            await asyncio.sleep(random.random() * 0.05)

    async def run_test(self, namespaces):
        end_time = time.time() + self.duration
        tasks = [self.worker(ns, end_time) for ns in namespaces]
        await asyncio.gather(*tasks)
