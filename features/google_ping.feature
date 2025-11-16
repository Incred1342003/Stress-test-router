Feature: Internet Connectivity Testing Using Google DNS
  To verify that each virtual client can reach the internet,
  As a network tester,
  I want to test connectivity from every namespace to Google DNS (8.8.8.8).

  Background:
    Given the base network interface is available on the system

  @internet
  Scenario: Verify that clients can reach Google DNS
    Given I create 10 virtual clients using macvlan
    Then each client should receive a valid IP address from the router
    And no two clients should receive the same IP address
    And all assigned IPs should be reachable
    When all clients attempt to ping Google DNS
    Then each client should successfully reach the internet
