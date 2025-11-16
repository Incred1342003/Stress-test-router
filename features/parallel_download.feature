Feature: High-Load Parallel File Download Stress Testing
  This feature validates whether the router and underlying network infrastructure
  can sustain high-bandwidth outbound traffic when multiple virtual clients attempt
  to download large files in parallel. Each virtual client is created using macvlan
  and is expected to perform a high-volume download of a 100GB ZIP file from a 
  predefined HTTP server.

  Goals of this stress test include:
    - Evaluating router stability under sustained heavy load.
    - Measuring concurrent throughput across multiple namespaces.
    - Ensuring clients remain connected without timeouts or download failures.
    - Identifying bandwidth limitations and bottlenecks.
    - Observing whether increasing client count impacts network performance.

  Background:
    Given the base network interface is available on the system
    And a 100GB ZIP file URL is configured as the download source
    And the host machine can reach the download server

  @download @stress
  Scenario Outline: Validate parallel high-volume file downloads for multiple virtual clients
    Given I create <client_count> virtual clients using macvlan
    Then each client should receive a valid IP address from the router
    And no two clients should receive the same IP address
    And all assigned IPs should be reachable
    When all clients start downloading the 100GB ZIP file simultaneously
    Then every client should successfully download the file
    And no client should experience a download interruption
    And a detailed download performance report should be generated

    Examples:
      | client_count |
      | 2            |
      | 5            |
      | 10           |
      | 20           |
