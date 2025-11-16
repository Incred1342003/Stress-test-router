import asyncio
from behave import given, when, then
from utils.logger import logger
from src.download_manager import DownloadManager


@when("all clients start downloading the 100GB ZIP file simultaneously")
def step_start_parallel_download(context):
    logger.info("----- PARALLEL DOWNLOAD STARTED -----")

    dm = DownloadManager(
        url=context.download_url,
        timeout=context.config.get("download_timeout")
    )

    # Run in parallel and store results
    context.download_results = asyncio.run(
        dm.start_parallel_download(context.net_mgr.client_namespaces)
    )

    logger.info("----- PARALLEL DOWNLOAD ENDED -----")


@then("every client should successfully download the file")
def step_validate_success(context):
    failed = [ns for ns, r in context.download_results.items() if not r["success"]]
    assert not failed, f"Clients with failed downloads: {failed}"


@then("no client should experience a download interruption")
def step_validate_no_interruptions(context):
    interrupted = [ns for ns, r in context.download_results.items() if r["interrupted"]]
    assert not interrupted, f"Clients with interruptions: {interrupted}"


@then("the router should remain responsive throughout the process")
def step_validate_responsiveness(context):
    # Simple router health check
    response = asyncio.run(
        context.net_mgr.ping_router_once()
    )
    assert response, "Router became unresponsive during download stress test"


@then("a detailed download performance report should be generated")
def step_generate_report(context):
    logger.info("Generating download performance report...")
    for ns, data in context.download_results.items():
        logger.info(f"{ns}: {data}")
