import paramiko
import time
import re
from utils.logger import logger


class RouterSSHManager:
    def __init__(self, host, username, password, timeout=10):
        self.host = host
        self.username = username
        self.password = password
        self.timeout = timeout
        self.ssh = None
        self.shell = None

        # Metrics Trackers
        self.cpu_readings = []
        self.current_session_peak_cpu = 0.0

    def connect(self):
        if self.ssh:
            return
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.host, username=self.username, password=self.password, timeout=self.timeout)
            self.shell = self.ssh.invoke_shell()
            self.shell.settimeout(2)
            logger.info(f"Connected to {self.host}")
        except Exception as e:
            logger.error(f"SSH Auth Failed: {e}")

    def run_in_shell(self, command):
        if not self.shell:
            self.connect()
        try:
            self.shell.send(command + "\n")
            time.sleep(0.7)
            output = self.shell.recv(65535).decode(errors="ignore")
            return output.strip()
        except Exception:
            return ""

    def get_health(self):
        """Captures CPU metrics and updates trackers."""
        raw = self.run_in_shell("top -bn1 | grep 'CPU:'")

        cpu_usage_val = 0.0
        # Try to find active usage directly (non-idle)
        usage_match = re.search(r"(\d+)%\s+(?!idle)", raw)
        idle_match = re.search(r"(\d+)%\s+idle", raw)

        if usage_match:
            cpu_usage_val = float(usage_match.group(1))
        elif idle_match:
            cpu_usage_val = 100.0 - float(idle_match.group(1))

        if cpu_usage_val > 0 or idle_match:
            self.cpu_readings.append(cpu_usage_val)
            if cpu_usage_val > self.current_session_peak_cpu:
                self.current_session_peak_cpu = cpu_usage_val

        # IMPORTANT: Log this so it appears in the realtime_report.log
        logger.info(f"[ROUTER] CPU: {cpu_usage_val}%")
        return cpu_usage_val

    def get_router_version(self):
        output = self.run_in_shell("cat /etc/banner")
        if "6E" in output or "6ghz" in output.lower():
            return "Router_6E"
        if "WiFi 6" in output or "ax" in output.lower():
            return "Router_6"
        return "Router_5"

    def disconnect(self):
        if self.ssh:
            self.ssh.close()
