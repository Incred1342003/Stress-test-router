Feature: Multiple client starts parallely streaming youtube viedo.

  Background:
    Given the base network interface is available on the system

  Scenario: Create multiple virtual clients and verify connectivity
    Given I create 5 virtual clients using macvlan
    Then no two clients should receive the same IP address
    And all assigned IPs should be reachable