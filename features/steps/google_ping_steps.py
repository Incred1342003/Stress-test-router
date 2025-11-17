import asyncio
from behave import when, then
from src.ping_manager import PingManager
from utils.logger import logger


@when('all clients attempt to ping Google DNS')
def step_ping_google(context):
    logger.info("------ PARALLEL CLIENT PING TO GOOGLE DNS STARTED -----")

    google_dns_ip = "8.8.8.8"
    ping_duration = context.config.get("ping_duration")

    pm = PingManager(google_dns_ip, ping_duration)
    context.results = asyncio.run(
        pm.run_test([ns for ns in context.net_mgr.client_namespaces])
    )

    logger.info("----- STOPPED PING TO GOOGLE DNS -----")


@then('each client should successfully reach the internet')
def step_validate_ping(context):
    failed = [ns for ns, success in context.results.items() if not success]

    assert len(failed) == 0, f"Clients failed to reach Google DNS: {', '.join(failed)}"

    logger.info("All clients successfully reached Google DNS.")
