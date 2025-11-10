import asyncio
import time
from utils.logger import logger
import subprocess
from unittest import SkipTest

class NetworkManager:
    def __init__(self, parent_if="eth0"):
        self.parent_if = parent_if
        self.client_namespaces = []
        self.client_ips = {}
        self.isFailed = False
        self.count = 0

    async def run_cmd(self, cmd):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError(proc.returncode, cmd, output=stdout, stderr=stderr)
        return stdout.decode()

    async def wait_for_ip(self, namespace, interface, timeout=2):
        start = time.time()
        while time.time() - start < timeout:
            try:
                output = await self.run_cmd(f"sudo ip netns exec {namespace} ip -4 addr show {interface}")
                if "inet " in output:
                    ip = output.split("inet ")[1].split()[0]
                    logger.info(f"{namespace} got IP: {ip}")
                    self.client_ips[namespace] = ip
                    return True
            except subprocess.CalledProcessError:
                await asyncio.sleep(0.5)
        logger.warning(f"{namespace} did not get IP within {timeout}s.")
        return False

    async def cleanup(self):
        logger.info("----- IP is Not Alloated to some client, Aborting -----")
        try:
            output = await self.run_cmd("sudo ip netns list")
            namespaces = [line.split()[0] for line in output.splitlines() if line]

            for ns in namespaces:
                macvlan = f"macvlan{ns[2:]}"
                try:
                    output = await self.run_cmd(f"sudo ip netns exec {ns} ip -4 addr show {macvlan}")
                    if "inet " in output:
                        await self.run_cmd(
                            f"sudo ip netns exec {ns} dhclient -r {macvlan} "
                            f"-pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases"
                        )
                    await self.run_cmd(f"sudo ip netns delete {ns}")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to delete {ns}: {e}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list namespaces: {e}")
        logger.info("All client deleted Successfully that was created")

    async def create_client(self, i):
        ns = f"ns{i}"
        macvlan = f"macvlan{i}"
        mac = f"00:1A:79:{(i >> 8) & 0xff:02x}:{(i >> 4) & 0xff:02x}:{i & 0xff:02x}"
        self.client_namespaces.append(ns)

        try:
            await self.run_cmd(f"sudo ip netns add {ns}")
            await self.run_cmd(f"sudo ip link add link {self.parent_if} {macvlan} address {mac} type macvlan mode bridge")
            await self.run_cmd(f"sudo ip link set {macvlan} netns {ns}")
            await self.run_cmd(f"sudo ip netns exec {ns} ip link set dev {macvlan} up")
            await self.run_cmd(f"sudo ip netns exec {ns} ip link set lo up")
            await self.run_cmd(
                f"sudo ip netns exec {ns} dhclient -v {macvlan} "
                f"-pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases &"
            )

            for attempt in range(4):
                if await self.wait_for_ip(ns, macvlan):
                    self.count+=1
                    return
                logger.warning(f"{ns} retrying IP acquisition ({attempt + 1}/4)...")
                await asyncio.sleep(1)

            self.isFailed = True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create {ns}: {e}")
            self.isFailed = True

    async def create_clients(self, count):
        tasks = [self.create_client(i) for i in range(1, count + 1)]
        await asyncio.gather(*tasks)
        logger.info(f"----- ONLY {self.count} / {count} got IP ------")
        self.count = 0
        if(self.isFailed):
            self.isFailed = False
            raise SkipTest("Skipping scenario due to failed client creation")
        logger.info(f"Created {count} namespaces successfully.")

    # def run_stress_client(self, ns, duration=30):
    #     logger.info(f"{ns}: starting real-world router stress for {duration}s")

    #     cmd = (
    #         f"sudo ip netns exec {ns} bash -c '"
    #         # # Massive parallel HTTP downloads
    #         # f"for i in {{1..50}}; do "
    #         # f"  (timeout {duration}s curl -s http://speed.hetzner.de/100MB.bin >/dev/null 2>&1 &) ; "
    #         # f"done; "
    #         # # Random DNS floods
    #         f"for i in {{1..1000}}; do "
    #         f"  (timeout {duration}s dig @8.8.8.8 google.com >/dev/null 2>&1 &) ; "
    #         f"done; "
    #         # # Continuous ICMP flood (to trigger QoS and ICMP handling)
    #         # f"ping -f -c 100000 8.8.8.8 >/dev/null 2>&1 &'"
    #         "'"
    #     )

    #     return subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
