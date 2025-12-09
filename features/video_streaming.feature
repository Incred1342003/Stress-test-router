Feature: High-Load Video Streaming Stress Test
  To verify router performance under heavy multimedia load,
  As a network tester,
  I want all virtual clients to stream different YouTube videos simultaneously.

  Background:
    Given the base network interface is available on the system

  @video @stress @hardware
  Scenario: Stream video on multiple clients simultaneously
    Given I create "5" virtual clients using macvlan
    Then no two clients should receive the same IP address
    And all assigned IPs should be reachable
    When all clients start streaming a video simultaneously
    Then each client should successfully stream for the given duration
