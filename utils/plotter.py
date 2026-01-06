import re
import os
import matplotlib.pyplot as plt


def save_graph(fig, filename):
    """
    Save a graph as PNG in docs/docs/assets, overwriting old files.
    """
    path = os.path.join("docs", "docs", "assets", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def parse_log(log_file="network_stress_report.log"):
    """
    Parse the stress test log for Pi metrics, Router CPU, and Ping Summary.
    """
    pi_cpu, pi_temp, pi_ram, router_cpu = [], [], [], []
    namespaces, ping_latency, ping_speed = [], [], []

    with open(log_file) as f:
        for line in f:
            if "[PI" in line and "CPU=" in line:
                cpu = float(re.search(r"CPU=(\d+\.\d+)%", line).group(1))
                temp = float(re.search(r"Temp=(\d+\.\d+)C", line).group(1))
                ram = float(re.search(r"RAM=(\d+\.\d+)%", line).group(1))
                pi_cpu.append(cpu)
                pi_temp.append(temp)
                pi_ram.append(ram)
            elif "[ROUTER" in line and "CPU:" in line:
                usr_match = re.search(r"(\d+)% usr", line)
                sys_match = re.search(r"(\d+)% sys", line)
                if usr_match and sys_match:
                    usr = int(usr_match.group(1))
                    sys = int(sys_match.group(1))
                    router_cpu.append(usr + sys)
            elif line.strip().startswith("| ns") and "OK" in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 4:
                    try:
                        ns = parts[0]
                        latency = float(parts[2])
                        speed = float(parts[3])
                        namespaces.append(ns)
                        ping_latency.append(latency)
                        ping_speed.append(speed)
                    except ValueError:
                        pass

    return pi_cpu, pi_temp, pi_ram, router_cpu, namespaces, ping_latency, ping_speed


def generate_graphs():
    """
    Generate and save static PNG graphs for Pi metrics, Router CPU, and Ping Summary.
    """
    pi_cpu, pi_temp, pi_ram, router_cpu, ns, lat, spd = parse_log()

    if pi_cpu or pi_temp or pi_ram:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_axis = [i * 5 for i in range(len(pi_cpu))]
        ax.plot(x_axis, pi_cpu, label="CPU %", color="steelblue")
        ax.plot(x_axis, pi_temp, label="Temp °C", color="salmon")
        ax.plot(x_axis, pi_ram, label="RAM %", color="seagreen")
        ax.set_title("Raspberry Pi Resource Usage")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Usage")
        ax.legend()
        save_graph(fig, "pi_usage.png")

    if router_cpu:
        fig, ax = plt.subplots(figsize=(10, 6))
        x_axis = [i * 5 for i in range(len(router_cpu))]
        ax.plot(x_axis, router_cpu, label="Router CPU %", color="purple")
        ax.set_title("Router CPU Usage")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("CPU %")
        ax.legend()
        save_graph(fig, "router_cpu.png")

    if ns and lat:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(ns, lat, color="skyblue")
        ax.set_title("Ping Latency per Namespace")
        ax.set_xlabel("Namespaces/Clients")
        ax.set_ylabel("Latency (s)")
        save_graph(fig, "ping_latency.png")

    if ns and spd:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(ns, spd, color="lightgreen")
        ax.set_title("Ping Speed per Namespace")
        ax.set_xlabel("Namespaces/Clients")
        ax.set_ylabel("Speed (Mbps)")
        save_graph(fig, "ping_speed.png")

    print("Graphs generated successfully.")
