Feature: Internet Connectivity Testing Using Google DNS
  To verify that each virtual client can reach the internet,
  As a network tester,
  I want to test connectivity from every namespace to Google DNS (8.8.8.8).

  Background:
    Given the base network interface is available on the system

  @internet
  Scenario: Verify that clients can reach Google DNS
    Given I create 5 virtual clients using macvlan
    Then no two clients should receive the same IP address
    And all assigned IPs should be reachable
    When all clients attempt to ping Google DNS
    Then each client should successfully reach the internet

  @scalability
  Scenario Outline: Pinging Google.com with varying number of clients
    Given I create <client_count> virtual clients using macvlan
    Then no two clients should receive the same IP address
    And all assigned IPs should be reachable
    When all clients attempt to ping Google DNS
    Then each client should successfully reach the internet

    Examples:
      | client_count |
      | 10           |
      | 20           |
      | 50           |
      | 100          |
      | 200          |


