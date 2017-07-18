#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.link import Link
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( controller=RemoteController)

    info( '*** Adding controller\n' )
    c0=net.addController('c0', port=6633)

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', dpid='0000000000000001')
    s2 = net.addSwitch('s2', dpid='0000000000000002')

    info( '*** Add hosts\n')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None, mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None, mac='00:00:00:00:00:03')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None, mac='00:00:00:00:00:01')

    info( '*** Add links\n')
    Link(s1, h1)
    Link(s1, h2)
    Link(s1, s2)
    Link(s2, h3)

    info( '*** Starting network\n')
    net.build()

    info( '*** Starting controllers\n')
    c0.start()

    info( '*** Starting switches\n')
    s1.start([])
    s2.start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

