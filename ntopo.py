"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        nh1 = self.addHost( 'h1' )
        nh2 = self.addHost( 'h2' )
        nh3 = self.addHost('h3')
        ns1 = self.addSwitch( 's1' )
        ns2 = self.addSwitch( 's2' )
        ns3 = self.addSwitch( 's3' )
        ns4 = self.addSwitch( 's4' )

        # Add links
        self.addLink( nh1, ns1 )
        self.addLink(nh1, ns3)
        self.addLink( nh2, ns1 )
        self.addLink(nh2, ns4)
      #  self.addLink(ns2, ns1)
        self.addLink(ns1, ns2)
        self.addLink(ns2, ns3)
        self.addLink(ns2, ns4)
        self.addLink(nh3, ns3)
        self.addLink(nh1, ns4)


topos = { 'mytopo': ( lambda: MyTopo() ) }
