import asyncio
import subprocess
import time
from utils.logger import logger

async def run_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd, output=stdout, stderr=stderr)
    return stdout.decode()

async def cleanup_namespace(ns):
    macvlan = f"macvlan{ns[2:]}"
    try:
        await run_cmd(
            f"sudo ip netns exec {ns} dhclient -r {macvlan} "
            f"-pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases"
        )
        await run_cmd(f"sudo ip netns delete {ns}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to delete {ns}: {e}")


async def async_cleanup():
    logger.info("----- ASYNC CLEANUP STARTED -----")
    try:
        output = await run_cmd("sudo ip netns list")
        namespaces = [line.split()[0] for line in output.splitlines() if line]
        tasks = [cleanup_namespace(ns) for ns in namespaces]
        await asyncio.gather(*tasks)
        logger.info("All clients deleted successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to list namespaces: {e}")

def cleanup():
    asyncio.run(async_cleanup())

# -------------------------------
# Behave lifecycle hooks
# -------------------------------
def before_all(context):
    logger.info("----- STARTING NETWORK STRESS TEST -----")
    cleanup()

def before_scenario(context, scenario):
    logger.info("----- BEFORE SCENARIO CLEANING PROCESS STARTS -----")
    cleanup()
    logger.info("----- CLEANUP DONE SUCCESSFULLY -----")

def after_all(context):
    logger.info("----- END CLEANING PROCESS STARTS -----")
    cleanup()
    logger.info("----- CLEANUP DONE SUCCESSFULLY -----")