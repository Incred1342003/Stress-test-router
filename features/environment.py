from utils.logger import logger
import subprocess
from src.network_manager import NetworkManager
import time

def before_all(context):
    logger.info("----- STARTING NETWORK STRESS TEST -----")
    
def cleanup():
    output = subprocess.check_output("sudo ip netns list", shell=True).decode().strip()
    namespaces = [line.split()[0] for line in output.splitlines() if line]

    for i in range(len(namespaces)):
        ns = namespaces[i]
        try:
            macvlan = f"macvlan{ns[2:]}"
            subprocess.run(
                f"sudo ip netns exec {ns} dhclient -r {macvlan} -pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases", 
                shell=True,
                capture_output=True 
            )
            subprocess.run(f"sudo ip netns delete {ns}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to delete {ns}: {e}")
    logger.info("All client deleted Successfully")


def before_scenario(context, scenario):
    logger.info("----- BEFORE SCENARIO CLEANING PROCESS STARTS -----")
    cleanup()

def after_all(context):
    logger.info("----- END CLEANING PROCESS STARTS -----")
    cleanup()
