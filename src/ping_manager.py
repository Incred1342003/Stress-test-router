import threading, subprocess, time, random

class PingManager:
    def __init__(self, router_ip="192.168.1.1", duration=60, workers_per_ns=5, upstream="10.0.0.2"):
        self.router_ip = router_ip
        self.duration = duration
        self.workers_per_ns = workers_per_ns
        self.upstream = upstream

    def worker(self, ns, end_time):
        while time.time() < end_time:
            # 1) occasional DHCP churn
            # macvlan = f"macvlan{ns[2:]}"
            # if random.randint(0,19) == 0:
            #     subprocess.run(f"sudo ip netns exec {ns} dhclient -r {macvlan}", shell=True)
            #     subprocess.run(f"sudo ip netns exec {ns} dhclient -v {macvlan}", shell=True)

            # 2) short TCP connects to upstream (conntrack/NAT)
            subprocess.run(f"sudo ip netns exec {ns} timeout 1 bash -c 'for p in 80 443 8080 53; do nc -z -w 1 {self.upstream} $p >/dev/null 2>&1; done'", shell=True)

            # 3) DNS lookup to router
            subprocess.run(f"sudo ip netns exec {ns} dig @{self.router_ip} google.com +time=1 >/dev/null 2>&1", shell=True)

            time.sleep(random.random() * 0.05)

    def run_test(self, namespaces):
        end_time = time.time() + self.duration
        threads = []
        for ns in namespaces:
            for _ in range(self.workers_per_ns):
                t = threading.Thread(target=self.worker, args=(ns, end_time), daemon=True)
                t.start()
                threads.append(t)
        for t in threads:
            t.join()