#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from subprocess import call

x=raw_input("Enter host id to be added:")
y='h'+str(x)
net.addHost(y)
net.addLink(s1,net.get(y))
net.get('s1').attach('s1-eth'+str(x))
net.get(y).setIP('10.0.0.'+str(x)+'/8')
net.get(y)
net.get(y).cmd("xterm -hold -e sudo python /home/mansi/Desktop/merge1.py "+str(0)+" &")


# To run in mininet type : py execfile("addHostonfly.py")

