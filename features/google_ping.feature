Feature: Internet Connectivity Testing Using Google DNS
  To verify that each virtual client can reach the internet,
  As a network tester,
  I want to test connectivity from every namespace to Google DNS (8.8.8.8).

  Background:
    Given the router IP address is configured
    And the base network interface is available on the system

  @internet @hardware
  Scenario: Verify that clients can reach Google DNS
    Given I create 5 virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients attempt to ping Google DNS
    Then each client should successfully reach the internet

  @scalability @hardware
  Scenario Outline: Pinging Google.com with varying number of clients
    Given I create <client_count> virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients attempt to ping Google DNS
    Then each client should successfully reach the internet

    Examples:
      | client_count |
      | 5            |
