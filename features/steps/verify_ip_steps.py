from behave import then
from utils.logger import logger

@then("no two clients should receive duplicate IP addresses (IPv4 or IPv6)")
def step_no_duplicate_ips(context):
    all_ips = []
    for ns, ips in context.net_mgr.client_ips.items():
        if "ipv4" in ips:
            all_ips.append(ips["ipv4"])
        if "ipv6" in ips:
            all_ips.append(ips["ipv6"])
    duplicates = {ip for ip in all_ips if all_ips.count(ip) > 1}
    assert not duplicates, f"Duplicate IPs found: {duplicates}"
    logger.info("All clients received unique IPv4 and IPv6 addresses.")

@then("all assigned IPv4 and IPv6 addresses should be reachable")
def step_validate_ip_reachability(context):
    failed = []
    for ns, ips in context.net_mgr.client_ips.items():
        for label, ip in ips.items():
            ip_only = ip.split("/")[0]
            success = context.net_mgr.ping_ip_from_ns(ns, ip_only)
            if not success:
                failed.append(f"{ns} {label} ({ip_only})")
    assert not failed, f"Unreachable addresses: {', '.join(failed)}"
    # Only one clean summary line if all succeed
    logger.info("All assigned IPv4 and IPv6 addresses are reachable.")
