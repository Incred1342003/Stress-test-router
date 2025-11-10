Feature: Network Stress Testing via Virtual Clients
    I want to simulate multiple clients connecting via macvlan
    So that I can verify router DHCP and connectivity under load

    Scenario: Launch 10 clents and verify ping to router
        Given I create 10 clients connected to the router
        When All the client pinging parallel

    Scenario: Launch 10 clents and verify ping to router
        Given I create 10 clients connected to the router
        When All the client pinging parallel

    Scenario: Launch 10 clents and verify ping to router
        Given I create 10 clients connected to the router
        When All the client pinging parallel

    Scenario: Launch 10 clents and verify ping to router
        Given I create 10 clients connected to the router
        When All the client pinging parallel

      
