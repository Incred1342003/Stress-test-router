import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import logger

class StressTestPlotter:
    def __init__(self, router_version, router_ssh_manager, output_dir="docs/docs/assets"):
        self.router_version = router_version
        self.ssh_manager = router_ssh_manager
        self.log_file = f"results/realtime_log/{router_version}_report.log"
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        sns.set_theme(style="darkgrid")

    def _get_pi_metrics(self):
        metrics = []
        if not os.path.exists(self.log_file):
            return []
        # Matches exactly: [PI ] CPU=15.8% Temp=59.0C RAM=13.0%
        pattern = re.compile(r"CPU\s*=\s*(\d+\.?\d*)%.*?RAM\s*=\s*(\d+\.?\d*)%")
        with open(self.log_file, "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    metrics.append({"pi_cpu": float(match.group(1)), "pi_ram": float(match.group(2))})
        return metrics

    def plot_health(self):
        pi_data = self._get_pi_metrics()
        router_cpu = getattr(self.ssh_manager, 'cpu_readings', [])
        
        length = min(len(pi_data), len(router_cpu))
        if length == 0:
            logger.warning("Still no synchronized data. Ensure get_health() is called during test.")
            return

        df = pd.DataFrame({
            "Seconds": [i * 5 for i in range(length)],
            "Pi CPU %": [pi_data[i]["pi_cpu"] for i in range(length)],
            "Router CPU %": router_cpu[:length],
            "Pi RAM %": [pi_data[i]["pi_ram"] for i in range(length)]
        })

        plt.figure(figsize=(12, 6))
        sns.lineplot(data=df, x="Seconds", y="Pi CPU %", label="Pi CPU", marker="o", color="#00d1ff")
        sns.lineplot(data=df, x="Seconds", y="Router CPU %", label="Router CPU", marker="s", color="#ff8c00")
        sns.lineplot(data=df, x="Seconds", y="Pi RAM %", label="Pi RAM", linestyle="--", color="#32cd32")

        # Mark spikes above 90%
        for col in ["Pi CPU %", "Router CPU %"]:
            anomalies = df[df[col] >= 90.0]
            for _, row in anomalies.iterrows():
                plt.scatter(row["Seconds"], row[col], color="red", s=100, edgecolors="white", zorder=5)

        plt.title(f"Hardware Performance Health - {self.router_version}")
        plt.ylim(0, 110)
        plt.savefig(os.path.join(self.output_dir, f"{self.router_version}_system_health.png"))
        plt.close()

    def plot_speeds(self, ns_speed_dict):
        """Generates the Namespace Speed bar chart in MBps."""
        if not ns_speed_dict: return
        
        # Convert Mbps to MBps (Mbps / 8)
        df = pd.DataFrame([
            {"Namespace": ns, "Speed (MBps)": round(val / 8, 2)} 
            for ns, val in ns_speed_dict.items()
        ])
        
        plt.figure(figsize=(10, 5))
        sns.barplot(data=df, x="Namespace", y="Speed (MBps)", hue="Namespace", palette="viridis", legend=False)
        plt.title(f"Peak Namespace Performance (MBps) - {self.router_version}")
        plt.savefig(os.path.join(self.output_dir, f"{self.router_version}_ns_speeds.png"))
        plt.close()