import os
import yaml
import json
import asyncio
import logging
import subprocess
from dotenv import load_dotenv
from datetime import datetime
from utils.logger import logger, add_version_specific_file_handler
from utils.command_runner import run_cmd
from lib.router_ssh_manager import RouterSSHManager

summary_logger = None


def setup_summary_logger(router_version):
    """
    Sets up a version-specific summary logger.
    Clears the file ('w') for that specific version.
    """
    logger_name = f"summary_{router_version}"
    s_logger = logging.getLogger(logger_name)
    s_logger.setLevel(logging.INFO)
    s_logger.propagate = False

    if not s_logger.handlers:
        os.makedirs("results/logs", exist_ok=True)
        # Unique summary log based on hardware
        log_path = f"results/logs/{router_version}_summary.log"
        handler = logging.FileHandler(log_path, mode='w')
        formatter = logging.Formatter("%(asctime)s | %(message)s")
        handler.setFormatter(formatter)
        s_logger.addHandler(handler)

    return s_logger


async def cleanup_namespace(ns):
    macvlan = f"macvlan{ns[2:]}"
    try:
        await run_cmd(
            f"sudo ip netns exec {ns} dhclient -6 -r {macvlan} "
            f"-pf /run/dhclient6-{ns}.pid "
            f"-lf /var/lib/dhcp/dhclient6-{ns}.leases"
        )
        await run_cmd(
            f"sudo ip netns exec {ns} dhclient -r {macvlan} "
            f"-pf /run/dhclient-{ns}.pid "
            f"-lf /var/lib/dhcp/dhclient-{ns}.leases"
        )
        await run_cmd(f"sudo ip netns delete {ns}")
        await run_cmd(f"sudo rm -rf /etc/netns/{ns}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"Failed to clean up {ns}: {e}")


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


def before_all(context):
    global summary_logger

    # Initial console-only logging until hardware is detected
    logger.info("----- STARTING NETWORK STRESS TEST -----")

    try:
        load_dotenv()
        logger.info(".env file loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load .env file: {e}")
        raise AssertionError(f"Failed to load .env file: {e}")

    logger.info("----- EXECUTING SSH LOGIN SCRIPT -----")
    try:
        cmd = f"./script/ssh-login.py -i {os.getenv('ROUTER_MAC')}"
        subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.info("SSH login script executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"SSH login script failed: {e}")
        raise AssertionError(f"SSH login script failed: {e}")

    logger.info("----- CLEANING UP BEFORE STARTING TEST -----")
    cleanup()
    logger.info("----- CLEANUP DONE SUCCESSFULLY -----")

    logger.info("----- INITIALIZING ROUTER SSH MANAGER -----")
    context.router_ssh = RouterSSHManager(
        host=os.getenv("HOST"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        timeout=int(os.getenv("SSH_TIMEOUT", 10)),
    )

    try:
        context.router_ssh.connect()
        # DETECT HARDWARE VERSION
        context.router_version = context.router_ssh.get_router_version()
        logger.info(f"Router Version Detected: {context.router_version}")
    except Exception as e:
        logger.error(f"Failed to connect to router: {e}")
        raise AssertionError(f"Failed to Connect to router: {e}")

    # 1. TRIGGER REALTIME LOG FILE (Dynamic Name)
    add_version_specific_file_handler(context.router_version)

    # 2. INITIALIZE SUMMARY LOG (Dynamic Name)
    summary_logger = setup_summary_logger(context.router_version)
    summary_logger.info(f"Test Run Started for {context.router_version}:")

    # 3. INITIALIZE JSON FILE (Dynamic Name)
    os.makedirs("results/json", exist_ok=True)
    context.json_file = f"results/json/{context.router_version}_summary.json"
    with open(context.json_file, "w") as f:
        json.dump([], f)

    logger.info("----- LOADING CONFIGURATION -----")
    try:
        with open("config.yaml") as file:
            context.config = yaml.safe_load(file)
        logger.info("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise AssertionError(f"Failed to load configuration: {e}")


def before_scenario(context, scenario):
    logger.info("\n" + "----- BEFORE SCENARIO CLEANING PROCESS STARTS -----")
    cleanup()
    scenario.start_time = datetime.now().isoformat()
    logger.info("----- CLEANUP DONE SUCCESSFULLY -----")


def after_scenario(context, scenario):
    end_time = datetime.now().isoformat()
    steps_data = []
    failure_message = None

    for step in scenario.steps:
        step_info = {"name": step.name, "status": step.status.name}
        if step.status.name == "failed":
            step_info["failure_message"] = str(step.exception)
            failure_message = str(step.exception)
        elif step.status.name == "undefined":
            step_info["failure_message"] = "Step definition not found"
            failure_message = "Step definition not found"
        elif step.status.name == "skipped":
            step_info["failure_message"] = "Step skipped due to previous failure"
        steps_data.append(step_info)

    scenario_result = {
        "feature": scenario.feature.name,
        "scenario": scenario.name,
        "status": scenario.status.name,
        "steps": steps_data,
        "router_version": context.router_version,  # Added for record keeping
        "timestamps": {
            "start": getattr(scenario, 'start_time', datetime.now().isoformat()),
            "end": end_time,
        },
        "failure_message": failure_message,
    }

    # Save to version-specific JSON
    try:
        with open(context.json_file, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(scenario_result)

    with open(context.json_file, "w") as f:
        json.dump(data, f, indent=2)

    if summary_logger:
        summary_logger.info(
            f"Feature: {scenario.feature.name} | Scenario: {scenario.name} | "
            f"Status: {scenario.status.name} | Failure: {failure_message or 'None'}"
        )

    logger.info(f"Scenario '{scenario.name}' finished. Result: {scenario.status.name}")


def after_all(context):
    logger.info("----- GENERATING PERFORMANCE GRAPHS -----")

    try:
        from utils.plotter import StressTestPlotter

        plotter = StressTestPlotter(context.router_version, context.router_ssh)
        plotter.plot_health()
        ns_speeds = getattr(context, 'ns_speeds', {})
        plotter.plot_speeds(ns_speeds)

    except Exception as e:
        logger.error(f"Plotting failed: {e}")

    logger.info("----- END CLEANING PROCESS STARTS -----")
    cleanup()
    if hasattr(context, 'router_ssh'):
        context.router_ssh.disconnect()
