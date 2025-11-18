import asyncio
import time
from utils.logger import logger


async def run_cmd(cmd, suppress_output=False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=(
            asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE
        ),
        stderr=(
            asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE
        ),
    )
    stdout, stderr = await proc.communicate()

    return {
        "returncode": proc.returncode,
        "stdout": None if suppress_output else stdout.decode(),
        "stderr": None if suppress_output else stderr.decode(),
    }


class DownloadManager:
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

    async def worker(self, ns, results):
        cmd = (
            f"sudo ip netns exec {ns} "
            f"timeout {self.timeout} wget -q "
            f"-O /dev/null -o /dev/null "
            f"--no-cache {self.url}"
        )

        start = time.time()
        result = await run_cmd(cmd)

        duration = time.time() - start

        success = result["returncode"] == 0

        results[ns] = {
            "success": success,
            "duration": duration,
            "interrupted": not success,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
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
