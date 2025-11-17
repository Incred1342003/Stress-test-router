import asyncio
from behave import when, then
from src.ping_manager import PingManager
from utils.logger import logger

@when('all clients attempt to ping the router simultaneously')
def step_ping_clients(context):
    logger.info("------ PARALLEL CLIENT PING STARTED -----")

    ping_duration = context.config.get("ping_duration")

    pm = PingManager(context.router_ip, ping_duration)

    context.results = asyncio.run(
        pm.run_test([ns for ns in context.net_mgr.client_namespaces])
    )
    
    logger.info("----- STOPPED PING -----")


@then('each client should successfully reach the router')
def step_validate_client_connectivity(context):
    failed = [ns for ns, success in context.results.items() if not success]
    
    assert len(failed) == 0, f"Clients failed to reach router: {', '.join(failed)}"
    
    logger.info("All clients successfully reached the router.")


@then('the overall network connectivity should remain stable')
def step_network_stability(context):
    total_clients = len(context.results)
    successful_clients = sum(1 for success in context.results.values() if success)
    
    stability_ratio = successful_clients / total_clients
    assert stability_ratio >= 0.95, f"Network stability below threshold: {stability_ratio:.2%}"
    
    logger.info(f"Network stability is acceptable: {stability_ratio:.2%} of clients reached the router.")

