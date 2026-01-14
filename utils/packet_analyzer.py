import subprocess
import os
import time
import shlex
from utils.logger import logger

class PacketAutomator:
    def __init__(self, results_dir="results/captures"):
        self.results_dir = results_dir
        os.makedirs(self.results_dir, exist_ok=True)
        self.active_processes = {}

    def start_diagnostic_capture(self, ns, interface):
        """Starts a background pcap for the specific namespace."""
        file_path = f"{self.results_dir}/{ns}_diagnostic.pcap"
        # Capturing first 200 packets to diagnose handshake/connectivity issues
        cmd = f"sudo ip netns exec {ns} tcpdump -i {interface} -n -w {file_path} -c 200"
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.active_processes[ns] = {"proc": proc, "path": file_path}

    def analyze_failure(self, ns):
        """Versatile logic to determine the 'Root Cause' of the failure."""
        if ns not in self.active_processes:
            return "No capture data available for analysis."
        
        cap = self.active_processes[ns]
        # Stop the background tcpdump
        if cap["proc"].poll() is None:
            cap["proc"].terminate()
        
        time.sleep(1) # Wait for file buffer to sync
        pcap = cap["path"]

        if not os.path.exists(pcap) or os.path.getsize(pcap) == 0:
            return "PCAP file empty: Interface likely went down or no packets were sent."

        # 1. Check for ARP Failure (The most common Router_5 issue)
        # Filter: ARP requests with no replies
        arp_req = self._count_packets(pcap, "arp and arp[6:2] == 1")
        arp_rep = self._count_packets(pcap, "arp and arp[6:2] == 2")
        if arp_req > 0 and arp_rep == 0:
            return "ARP TIMEOUT: Namespace is asking for Router MAC, but Router is not responding."

        # 2. Check for DNS Failure
        dns_req = self._count_packets(pcap, "udp port 53")
        if dns_req > 0:
            dns_resp = self._count_packets(pcap, "udp port 53 and src port 53")
            if dns_resp == 0:
                return "DNS FAILURE: Queries sent to 8.8.8.8, but zero responses received."

        # 3. Check for Router Rejections (NAT/Firewall full)
        icmp_unreach = self._count_packets(pcap, "icmp[icmptype] == icmp-unreach")
        if icmp_unreach > 0:
            return "ROUTER REJECTION: Router explicitly sent 'Destination Unreachable' (NAT/Firewall likely full)."

        # 4. Check for TCP Issues (Handshake failures)
        tcp_syn = self._count_packets(pcap, "tcp[tcpflags] & tcp-syn != 0")
        tcp_ack = self._count_packets(pcap, "tcp[tcpflags] & tcp-ack != 0")
        if tcp_syn > 0 and tcp_ack == 0:
            return "TCP HANDSHAKE FAILURE: SYN sent, but no SYN-ACK received from server."

        return "GENERAL TIMEOUT: Packets transmitted (TX) but no ingress (RX) traffic seen from Gateway."

    def _count_packets(self, pcap_path, filter_str):
        """Helper to count packets using a tcpdump filter."""
        try:
            cmd = f"tcpdump -r {pcap_path} '{filter_str}' 2>/dev/null | wc -l"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            return int(result)
        except Exception:
            return 0