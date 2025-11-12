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

@when('All the client pinging parallel')
def ping_parallel(context):
    logger.info("------ PRALLEL CLIENT PING STARTED -----")
    pm = PingManager()
    asyncio.run(pm.run_test([ns for ns in context.net_mgr.client_namespaces]))
    logger.info("----- STOPPED PING -----")
