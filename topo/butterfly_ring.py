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
    s3 = net.addSwitch('s3', dpid='0000000000000003')
    s4 = net.addSwitch('s4', dpid='0000000000000004')
    s5 = net.addSwitch('s5', dpid='0000000000000005')
    s6 = net.addSwitch('s6', dpid='0000000000000006')
    s7 = net.addSwitch('s7', dpid='0000000000000007')

    h1 = net.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')
    h3 = net.addHost('h3', ip='10.0.0.3', mac='00:00:00:00:00:03')

    Link(s1, s2)
    Link(s1, s3)

    Link(s2, s4)
    Link(s2, s6)

    Link(s3, s4)
    Link(s3, s7)

    Link(s4, s5)

    Link(s5, s7)
    Link(s5, s6)

    Link(s6, h1)
    Link(s7, h2)
    Link(s1, h3)


    net.build()
    c0.start()
    s1.start([c0])
    #s2.start([c0])



    CLI(net)

    net.stop()