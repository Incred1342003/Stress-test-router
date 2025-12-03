Feature: High-Load Video Streaming Stress Test
  To verify router performance under heavy multimedia load,
  As a network tester,
  I want all virtual clients to stream different YouTube videos simultaneously.

  Background:
    Given the base network interface is available on the system

  @video @stress @hardware
  Scenario Outline: Stream video on multiple clients simultaneously
    Given I create <client_count> virtual clients using macvlan
    Then no two clients should receive duplicate IP addresses (IPv4 or IPv6)
    And all assigned IPv4 and IPv6 addresses should be reachable
    When all clients start streaming a video simultaneously
    Then each client should successfully stream for the given duration

    Examples:
      | client_count |
      |  20          |
