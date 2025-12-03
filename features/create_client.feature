Feature: Network Stress Testing Using Virtual Clients
  To ensure that the router performs reliably under heavy load,
  As a network tester,
  I want to automatically create multiple virtual clients using macvlan
  And verify that each client receives a valid IP and can reach the router.

  Background:
    Given the router IP address is configured
    And the base network interface is available on the system

  @stress_test @hardware
  Scenario: Create multiple virtual clients and verify connectivity
    Given I create 5 virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients attempt to ping the router simultaneously
    Then each client should successfully reach the router
    And the overall network connectivity should remain stable

  @scalability @hardware
  Scenario Outline: Stress test router with varying number of clients
    Given I create <client_count> virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients attempt to ping the router simultaneously
    Then each client should successfully reach the router

    Examples:
      | client_count |
      | 20           |
   
