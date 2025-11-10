Feature: Network Stress Testing via Virtual Clients
    I want to simulate multiple clients connecting via macvlan
    So that I can verify router DHCP and connectivity under load

    Scenario: Launch 5 clents and verify ping to router
        Given I create 5 clients connected to the router

      
