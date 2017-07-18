#!usr/bin/env python

from mininet.cli import CLI
from mininet.link import Link
from mininet.net import Mininet
from mininet.node import RemoteController

if '__main__' == __name__:
    net = Mininet(controller=RemoteController)

    c0 = net.addController('c0')

    s1 = net.addSwitch('s1', dpid='0000000000000001')
    s2 = net.addSwitch('s2', dpid='0000000000000002')

    h1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')

    Link(s1, h1)
    Link(s1, h2)
    Link(s1, s2)

    Link(s2, h3)



    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])



    CLI(net)

    net.stop()