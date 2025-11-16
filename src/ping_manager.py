import asyncio
import random
import time
from utils.logger import logger
from utils.command_runner import run_cmd

class PingManager:
    def __init__(self, target_ip, ping_duration):
        self.target_ip = target_ip
        self.duration = ping_duration

    async def worker(self, ns, end_time, results):
        """
        Runs continuous pings until duration expires.
        Records True/False in results dict for each namespace.
        """
        success = True  # assume success unless failure happens

        while time.time() < end_time:
            result = await run_cmd(
                f"sudo ip netns exec {ns} ping -c 1 -W 1 {self.target_ip}"
            )

            if result.returncode != 0:
                success = False
                logger.error(f"[FAIL] {ns} cannot reach router {self.target_ip}")
            else:
                logger.info(f"[OK] {ns} -> {self.target_ip} reachable")

            await asyncio.sleep(random.random() * 0.05)

        results[ns] = success

    async def run_test(self, namespaces):
        """
        Runs ping test on all namespaces and returns a dict:
        {
            "ns1": True,
            "ns2": False,
            ...
        }
        """
        end_time = time.time() + self.duration
        results = {}

        tasks = [
            self.worker(ns, end_time, results)
            for ns in namespaces
        ]

        await asyncio.gather(*tasks)
        return results





















# import asyncio
# import random
# import time
# from utils.logger import logger
# from utils.command_runner import run_cmd

# class PingManager:
#     def __init__(self, router_ip, ping_duration):
#         self.router_ip = router_ip
#         self.duration = ping_duration

#     async def worker(self, ns, end_time):
#         while time.time() < end_time:
#             await run_cmd(
#                 f"sudo ip netns exec {ns} ping -c 1 8.8.8.8"
#             )
#             await asyncio.sleep(random.random() * 0.05)

#     async def run_test(self, namespaces):
#         end_time = time.time() + self.duration
#         tasks = [self.worker(ns, end_time) for ns in namespaces]
#         await asyncio.gather(*tasks)
