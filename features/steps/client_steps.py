from behave import given, when, then
from src.network_manager import NetworkManager
from src.ping_manager import PingManager
from utils.logger import logger
import asyncio

@given('I create {count:d} clients connected to the router')
def step_create_clients(context, count):
    logger.info(f"--- GIVEN: Creating {count} Virtual Clients ---")
    context.net_mgr = NetworkManager()
    asyncio.run(context.net_mgr.create_clients(count))
    logger.info(f"STATUS: {count} clients successfully created and assigned IP addresses.")

# @when('All the client pinging parallel')
# def ping_parallel(context):
#     pm = PingManager(duration=60, workers_per_ns=5)
#     asyncio.run(pm.run_test([ns for ns in context.net_mgr.client_namespaces]))

 
# @when('all client performing heavy tasks')
# def heavy_task(context):
#     logger.info("--- WHEN: heavy load in Parallel")
#     context.ping_mgr = PingManager()
#     context.ping_mgr.run_test(context.net_mgr.client_namespaces)

    
# @when('I run a heavy network load in all clients for 1 minutes')
# def step_run_heavy_load(context):
#     duration_seconds = 60
#     logger.info(f"--- WHEN: Starting Heavy Network Load for {duration_seconds} seconds ---")
    
#     load_processes = []
#     for ns in context.net_mgr.client_namespaces:
#         procs = context.net_mgr.run_stress_client(ns, duration_seconds)
#         load_processes.append(procs)
#     for p in load_processes:
#         p.wait()
    
#     logger.info("Heavy network load phase completed.")



# @when('all clients ping the router in parallel')
# def step_ping_parallel(context):
#     logger.info("--- WHEN: Pinging Router in Parallel ---")
#     context.ping_mgr = PingManager(router_ip="192.168.1.1")
#     results = asyncio.run(context.ping_mgr.ping_all(context.net_mgr.client_namespaces))
#     context.ping_results = results

# @then('all clients should get successful responses')
# def step_validate_ping(context):
#     logger.info("--- THEN: Validating Ping Responses ---")
#     failed = [r for r in context.ping_results if not r['success']]
#     if failed:
#         logger.error(f"VERIFICATION FAILED: {len(failed)} clients failed to ping router.")
#         logger.error(f"FAILED CLIENTS: {[f['client'] for f in failed]}")
#         raise AssertionError(f"{len(failed)} clients failed to ping router.")
#     else:
#         logger.info(f"VERIFICATION SUCCESS: All {len(context.ping_results)} clients successfully pinged the router.")
