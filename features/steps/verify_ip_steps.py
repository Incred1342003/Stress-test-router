import re
from behave import then
from utils.logger import logger


def extract_ip(output):
    """Extract IPv4 address from ip addr show."""
    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/', output)
    return match.group(1) if match else None


@then("each client should receive a valid IP address from the router")
def step_validate_client_ips(context):
    context.client_ips = {}  # store namespace → IP

    for ns in context.net_mgr.client_namespaces:
        logger.info(f"Checking IP for namespace: {ns}")

        result = context.net_mgr.get_namespace_ip(ns)
        ip = extract_ip(result)

        assert ip, f"Client {ns} did not receive an IP address!"
        logger.info(f"{ns} --> assigned IP: {ip}")

        context.client_ips[ns] = ip


@then("no two clients should receive the same IP address")
def step_no_duplicate_ips(context):
    ips = list(context.client_ips.values())
    duplicates = set([x for x in ips if ips.count(x) > 1])

    assert len(duplicates) == 0, f"Duplicate IPs found: {duplicates}"
    logger.info("All clients received unique IPs.")


@then("all assigned IPs should be reachable")
def step_validate_ip_reachability(context):
    for ns, ip in context.client_ips.items():
        logger.info(f"Pinging {ip} from namespace {ns}")

        success = context.net_mgr.ping_ip_from_ns(ns, ip)
        assert success, f"{ns} could not ping its own assigned IP ({ip})"

    logger.info("All assigned IPs are reachable.")
