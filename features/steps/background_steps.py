from behave import given
import os

@given("the router IP address is configured")
def step_router_ip_configured(context):
    router_ip = context.config.get("router_ip")
    assert router_ip is not None, "Router IP address is not configured."
    context.router_ip = router_ip



@given("the base network interface is available on the system")
def step_interface_available(context):
    interface = context.config.get("interface")
    assert interface is not None, "Interface is not specified in the configuration."
    
    # Check if the interface exists on the system
    result = os.system(f"ip link show {interface} > /dev/null 2>&1")
    assert result == 0, f"Network interface {interface} is not available on the system."
    
    context.base_interface = interface



@given("a 100GB ZIP file URL is configured as the download source")
def step_configure_file_url(context):
    context.download_url = context.config.get("download_url")
    assert context.download_url, "Download URL missing in config!"