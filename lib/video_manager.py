import asyncio
import time
import subprocess
from utils.logger import logger
from utils.pi_health_check import health_worker
from utils.command_runner import run_cmd


class VideoManager:
    def __init__(self, video_map: dict[str, str], duration: int):
        # video_map is a dict: {video_id: title}
        self.video_map = video_map
        self.duration = duration
        # Keep a list of IDs for round-robin assignment
        self.video_ids = list(video_map.keys())

    async def _stream_with_mpv(self, ns: str, video_id: str) -> dict:
        url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = (
            f"sudo ip netns exec {ns} "
            f"timeout {self.duration}s "
            f"mpv --ytdl-format=bestvideo+bestaudio "
            f"--ao=null --vo=null --no-terminal --no-cache "
            f"{url}"
        )
        start_ts = time.time()
        success = False
        try:
            await run_cmd(cmd, suppress_output=True)
            success = True
        except subprocess.CalledProcessError as e:
            if e.returncode in (124, 143):  # timeout exit codes
                success = True
            else:
                logger.error(f"[ERROR] {ns} mpv crashed with code {e.returncode}")
        except Exception as e:
            logger.error(f"[ERROR] {ns} mpv exception: {e}")
        elapsed = time.time() - start_ts
        if elapsed < (self.duration * 0.9):
            success = False
        return {
            "success": success,
            "duration": elapsed,
            "video_id": video_id,
            "title": self.video_map.get(video_id, video_id),
        }

    async def start_parallel_streaming(self, namespaces: list[str]) -> dict:
        stop_event = asyncio.Event()
        health_task = asyncio.create_task(health_worker(stop_event))

        # Launch streaming tasks
        tasks = [
            self._stream_with_mpv(ns, self.video_ids[i % len(self.video_ids)])
            for i, ns in enumerate(namespaces)
        ]
        results_list = await asyncio.gather(*tasks)

        stop_event.set()
        await health_task

        results = {ns: res for ns, res in zip(namespaces, results_list)}

        # Log results sequentially AFTER all tasks finish
        logger.info("----- STREAMING RESULTS -----")
        for ns, res in results.items():
            title = res["title"]
            dur = res["duration"]
            if res["success"]:
                logger.info(f"[OK] {ns} streamed {title} for {dur:.2f} secs")
            else:
                logger.error(f"[FAIL] {ns} failed ({dur:.2f} secs)")

        return results
