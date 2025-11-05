import subprocess
import time
from utils.logger import logger
import os

class NetworkManger:
    def __init__(self, parent_if="eth0"):
        self.parent_if = parent_if
        self.client_namespaces = []
        self.client_ips = {}

    def run_cmd(self, cmd):
        subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True
        )

    def wait_for_ip(self, namespace, interface, timeout=2):
        start = time.time()
        while time.time() - start < timeout:
            try:
                output = subprocess.check_output(
                    f"sudo ip netns exec {namespace} ip -4 addr show {interface}",
                    shell=True
                ).decode()
                if "inet " in output:
                    ip = output.split("inet ")[1].split()[0]
                    logger.info(f"{namespace} got IP: {ip}")
                    self.client_ips[namespace] = ip
                    return True
            except subprocess.CalledProcessError:
                pass
        logger.warning(f"{namespace} did not get IP within {timeout}s.")
        return False

    def create_clients(self, count):
        for i in range(1, count + 1):
            ns = f"ns{i}"
            macvlan = f"macvlan{i}"
            mac = f"00:00:00:12:11:{i:02x}"
            self.client_namespaces.append(ns) 

            try:
                self.run_cmd(f"sudo ip netns add {ns}")
                self.run_cmd(f"sudo ip link add link eth0 {macvlan} address {mac} type macvlan mode bridge")
                self.run_cmd(f"sudo ip link set {macvlan} netns {ns}")
                self.run_cmd(f"sudo ip netns exec {ns} ip link set dev {macvlan} up")
                self.run_cmd(f"sudo ip netns exec {ns} ip link set lo up")
                self.run_cmd(f"sudo ip netns exec {ns} dhclient -v {macvlan} -pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases &")
                self.wait_for_ip(ns, macvlan)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to create {ns}: {e}")
                continue

        logger.info(f"Created {count} namespaces successfully.")



    def run_stress_client(self, ns, duration=30):
        logger.info(f"{ns}: starting real-world router stress for {duration}s")

        cmd = (
            f"sudo ip netns exec {ns} bash -c '"
            # # Massive parallel HTTP downloads
            # f"for i in {{1..50}}; do "
            # f"  (timeout {duration}s curl -s http://speed.hetzner.de/100MB.bin >/dev/null 2>&1 &) ; "
            # f"done; "
            # # Random DNS floods
            f"for i in {{1..1000}}; do "
            f"  (timeout {duration}s dig @8.8.8.8 google.com >/dev/null 2>&1 &) ; "
            f"done; "
            # # Continuous ICMP flood (to trigger QoS and ICMP handling)
            # f"ping -f -c 100000 8.8.8.8 >/dev/null 2>&1 &'"
            "'"
        )

        return subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)











    # def run_stress_client(self, ns, duration=30):
    #     target_ip = "8.8.8.8"  # or some public IP that ensures router does NAT
    #     processes = []

    #     # 1️⃣ Parallel ICMP floods (low level)
    #     ping_cmd = f"sudo ip netns exec {ns} ping -f -i 0.0001 -c 100000 {target_ip}"
    #     processes.append(subprocess.Popen(ping_cmd, shell=True,
    #                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    #     # 2️⃣ Parallel TCP floods (small bursts)
    #     tcp_cmd = (
    #         f"sudo ip netns exec {ns} bash -c "
    #         f"'for i in {{1..200}}; do "
    #         f"  (timeout {duration}s curl -s http://speed.hetzner.de/100MB.bin >/dev/null 2>&1 &) ; "
    #         f"done; wait'"
    #     )
    #     processes.append(subprocess.Popen(tcp_cmd, shell=True,
    #                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    #     # 3️⃣ UDP/iperf random load
    #     iperf_cmd = f"sudo ip netns exec {ns} iperf3 -u -b 100M -c {target_ip} -t {duration}"
    #     processes.append(subprocess.Popen(iperf_cmd, shell=True,
    #                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    #     logger.info(f"{ns}: launched mixed NAT-heavy load for {duration}s.")
    #     return processes




























    # def run_stress_client(self, ns, duration=30):
    #     laptop_ip = "192.168.1.7"
    #     cmd = (
    #         f"sudo ip netns exec {ns} iperf3 -c {laptop_ip} "
    #         f"-t {duration} "
    #         f"-P 8 -O 3"
    #     )
    #     return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)