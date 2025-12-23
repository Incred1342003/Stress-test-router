import asyncio
import time

from prettytable import PrettyTable
from utils.logger import logger
from utils.pi_health_check import health_worker


async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return {
        "returncode": proc.returncode,
        "stdout": stdout.decode().strip() if stdout else "",
        "stderr": stderr.decode().strip() if stderr else "",
    }


async def get_router_health(router_ssh, host, username, password, stop_event):
    while not stop_event.is_set():
        router_ssh.get_health()
        await asyncio.sleep(5)


class VideoManager:
    def __init__(self, router_ssh, video_ids: list[str], duration: int):
        self.router_ssh = router_ssh
        self.video_ids = video_ids
        self.duration = duration

    async def _get_ns_bytes(self, ns):
        cmd = f"sudo ip netns exec {ns} sh -c 'cat /sys/class/net/$(ls /sys/class/net | grep -v lo)/statistics/rx_bytes'"  # noqa: E501
        result = await run_cmd(cmd)
        return int(result["stdout"]) if result["stdout"].isdigit() else 0

    async def _stream_with_mpv(self, ns: str, video_id: str, results: dict):
        url = f"https://www.youtube.com/watch?v={video_id}"
        bytes_before = await self._get_ns_bytes(ns)

        cmd = (
            f"sudo ip netns exec {ns} "
            f"timeout {self.duration}s "
            f"mpv --ytdl-format=bestvideo+bestaudio "
            f"--ao=null --vo=null --no-terminal --no-cache "
            f"{url}"
        )

        start_time = time.time()
        result = await run_cmd(cmd)
        duration_taken = time.time() - start_time
        bytes_after = await self._get_ns_bytes(ns)

        is_success = result["returncode"] in [0, 124]

        total_bits = (bytes_after - bytes_before) * 8
        exact_speed = (
            total_bits / (duration_taken * 1024 * 1024) if duration_taken > 0 else 0
        )

        results[ns] = {
            "success": is_success,
            "duration": round(duration_taken, 2),
            "speed": round(exact_speed, 2),
            "video_id": video_id,
            "error": "" if is_success else f"Error {result['returncode']}",
        }

    def display_results(self, results):
        table = PrettyTable()

        table.field_names = [
            "Namespace",
            "Status",
            "Time (s)",
            "Speed (Mbps)",
            "Video ID",
            "Remarks",
        ]
        table.align["Namespace"] = "l"
        table.align["Status"] = "c"
        table.align["Remarks"] = "l"

        success_count = 0
        for ns, data in sorted(results.items()):
            status = "OK" if data["success"] else "FAIL"
            speed = data["speed"]

            if not data["success"]:
                remark = "Stream Failed / Timeout"
            elif speed < 0.5:
                remark = "Poor: Constant Buffering"
            elif speed < 1.5:
                remark = "Fair: SD Quality (480p)"
            elif speed < 4.0:
                remark = "Good: HD Quality (720p)"
            elif speed < 15.0:
                remark = "Excellent: FHD (1080p)"
            else:
                remark = "Ideal: 4K UHD Streaming"

            if data["success"]:
                success_count += 1

            table.add_row(
                [ns, status, data["duration"], speed, data["video_id"], remark]
            )

        logger.info(
            "\n"
            + "═" * 105
            + "\n"
            + f"VIDEO SUMMARY | SUCCESS: {success_count}/{len(results)}"
            + "\n"
            + "═" * 105
        )
        logger.info(f"\n {table}\n" + "═" * 105 + "\n")

    async def start_parallel_streaming(self, namespaces: list[str]) -> dict:
        results = {}
        stop_event_pi = asyncio.Event()
        stop_event_router = asyncio.Event()

        tasks = [
            self._stream_with_mpv(ns, self.video_ids[i % len(self.video_ids)], results)
            for i, ns in enumerate(namespaces)
        ]

        pi_task = asyncio.create_task(health_worker(stop_event_pi))
        router_task = asyncio.create_task(
            get_router_health(
                self.router_ssh,
                "192.168.1.1",
                "operator",
                "Charter123",
                stop_event_router,
            )
        )

        await asyncio.gather(*tasks)

        stop_event_pi.set()
        stop_event_router.set()
        await pi_task
        await router_task

        self.display_results(results)
        return results
