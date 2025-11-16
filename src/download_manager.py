import asyncio
import time
from utils.logger import logger
from utils.command_runner import run_cmd


class DownloadManager:
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

    async def worker(self, ns, results):
        """
        Each namespace downloads the file independently.
        Captures:
          - success/failure
          - bytes downloaded
          - time taken
          - any interruptions
        """
        start = time.time()
        cmd = (
            f"sudo ip netns exec {ns} wget -O /dev/null "
            f"--timeout={self.timeout} {self.url}"
        )

        logger.info(f"[START] {ns} downloading...")

        result = await run_cmd(cmd)

        duration = time.time() - start
        success = (result.returncode == 0)

        results[ns] = {
            "success": success,
            "duration": duration,
            "interrupted": not success,
            "stdout": result.stdout.decode("utf-8", errors="ignore"),
            "stderr": result.stderr.decode("utf-8", errors="ignore"),
        }

        if success:
            logger.info(f"[OK] {ns} completed download in {duration:.2f} sec")
        else:
            logger.error(f"[FAIL] {ns} download failed after {duration:.2f} sec")

    async def start_parallel_download(self, namespaces):
        results = {}
        tasks = [self.worker(ns, results) for ns in namespaces]
        await asyncio.gather(*tasks)
        return results
