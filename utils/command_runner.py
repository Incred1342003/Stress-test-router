import asyncio
import subprocess

async def run_cmd(cmd, suppress_output=False):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL if suppress_output else asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if not suppress_output and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, output=stdout, stderr=stderr)
    return None if suppress_output else stdout.decode()
