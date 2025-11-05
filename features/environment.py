from utils.logger import logger
import subprocess
from src.network_manager import NetworkManger
import time

def before_all(context):
    logger.info("Starting Network Stress Test Suite...")
    

def release_all_leases():
    output = subprocess.check_output("sudo ip netns list", shell=True).decode().strip()
    namespaces = [line.split()[0] for line in output.splitlines() if line]

    for i in range(len(namespaces)):
        ns = namespaces[i]
        try:
            macvlan = f"macvlan{ns[2:]}"
            subprocess.run(
                f"sudo ip netns exec {ns} dhclient -r {macvlan} -pf /run/dhclient-{ns}.pid -lf /var/lib/dhcp/dhclient-{ns}.leases", 
                shell=True,
                check=True,  # This will raise an error if dhclient fails
                # capture_output=True # Hides dhclient output from your main log
            )
            subprocess.run(f"sudo ip netns delete {ns}", shell=True, check=True)
            logger.info(f"Deleted namespace: {ns}")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to delete {ns}: {e}")
# def before_scenario(context, scenario):
#     release_all_leases()

#     logger.info(f"Cleaned old namespaces and killed background processes before scenario: {scenario.name}")

def after_all(context):
    print("--- AFTER_ALL FUNCTION IS RUNNING (THIS WILL ONLY APPEAR ONCE) ---")
    logger.info("Cleaning up network namespaces....")

    release_all_leases()
    logger.info("All namespaces deleted. Test suite complete.")
