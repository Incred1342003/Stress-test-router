import asyncio
import concurrent.futures
import random
import time

from prettytable import PrettyTable
from utils.command_runner import run_cmd
from utils.logger import logger
from utils.pi_health_check import health_worker


async def get_router_health(router_ssh, stop_event):
    """Background task to fetch router resources every 5 seconds."""
    while not stop_event.is_set():
        router_ssh.get_health()
        await asyncio.sleep(5)


class StressScenarioManager:
    def __init__(
        self,
        router_ssh,
        duration,
        download_url,
        router_ip="192.168.1.1",
        dns_server="8.8.8.8",
    ):
        self.router_ssh = router_ssh
        self.duration = duration
        self.download_url = download_url
        self.router_ip = router_ip
        self.dns_server = dns_server
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

    def _run_task_blocking(self, ns, task_func, end_time, result_dict):
        count = 0
        start_t = time.time()
        while time.time() < end_time:
            task_func(ns)
            count += 1

        result_dict[ns] = {
            "task": task_func.__name__.replace('_', ' ').strip(),
            "count": count,
            "duration": round(time.time() - start_t, 2),
        }

    def _dns_query(self, ns):
        run_cmd(
            f"sudo ip netns exec {ns} dig +time=1 google.com @{self.dns_server}",
            suppress_output=True,
        )

    def _tcp_connect(self, ns):
        run_cmd(
            f"sudo ip netns exec {ns} sh -c 'exec 3<>/dev/tcp/{self.router_ip}/80; exec 3<&-; exec 3>&-'",  # noqa: E501
            suppress_output=True,
        )

    def _http_router_hit(self, ns):
        run_cmd(
            f"sudo ip netns exec {ns} curl -m 2 -s -o /dev/null http://{self.router_ip}/",  # noqa: E501
            suppress_output=True,
        )

    def display_results(self, results):
        table = PrettyTable()
        table.field_names = [
            "Namespace",
            "Stress Task",
            "Total Hits",
            "Time (s)",
            "Rate (Hit/s)",
        ]
        table.align["Namespace"] = "l"
        table.align["Stress Task"] = "l"

        for ns, data in sorted(results.items()):
            rate = (
                round(data["count"] / data["duration"], 2)
                if data["duration"] > 0
                else 0
            )
            table.add_row([ns, data["task"], data["count"], data["duration"], rate])

        logger.info(
            "\n"
            + "═" * 80
            + "\n"
            + f"STRESS SCENARIO SUMMARY | DURATION: {self.duration}s"
            + "\n"
            + "═" * 80
        )
        logger.info(f"\n {table}\n" + "═" * 80 + "\n")

    async def start(self, namespaces):
        logger.info("======= STRESS TEST START =======")
        start_time = time.time()
        end_time = start_time + self.duration

        tasks = [self._dns_query, self._tcp_connect, self._http_router_hit]
        assigned = {ns: random.choice(tasks) for ns in namespaces}

        for ns, func in assigned.items():
            logger.info(f"{ns}: Assigned Task → {func.__name__}")

        result_dict = {}
        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        pi_task = asyncio.create_task(health_worker(stop_event))
        router_task = asyncio.create_task(
            get_router_health(self.router_ssh, stop_event)
        )

        futures = [
            loop.run_in_executor(
                self.executor,
                self._run_task_blocking,
                ns,
                assigned[ns],
                end_time,
                result_dict,
            )
            for ns in namespaces
        ]

        await asyncio.gather(*futures)

        stop_event.set()
        await asyncio.gather(pi_task, router_task)

        self.display_results(result_dict)
        return result_dict
