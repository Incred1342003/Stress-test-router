Feature: Parallel File Download Stress Testing
  This feature validates whether the router and underlying network infrastructure
  can sustain outbound traffic when multiple virtual clients attempt
  to download files in parallel. Each virtual client is created using macvlan
  and is expected to perform a medium-volume download of a 20MB ZIP file
  from a predefined HTTP server.

  Goals of this stress test include:
    - Evaluating router stability under concurrent load.
    - Measuring throughput across multiple namespaces.
    - Ensuring clients remain connected without timeouts or download failures.
    - Observing whether increasing client count impacts network performance.

  Background:
    Given the base network interface is available on the system
    And a 20MB ZIP file URL is configured as the download source

  @download @stress @hardware
  Scenario Outline: Validate parallel file downloads for multiple virtual clients
    Given I create <client_count> virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients start downloading the 20MB ZIP file simultaneously

    Examples:
      | client_count |
      | 5           |
