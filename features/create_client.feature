Feature: Network Stress Testing via Virtual Clients
    I want to simulate multiple clients connecting via macvlan
    So that I can verify router DHCP and connectivity under load

    Scenario: Launch 2 clents and verify ping to router
        Given I create 2 clients connected to the router
      
