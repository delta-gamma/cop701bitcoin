#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from subprocess import call
import re

class SingleSwitchTopo(Topo):
    "Single switch connected to n hosts."
    def build(self, n=2):
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)

def simpleTest():
    "Create and test a simple network"
    
    numnodes_pattern = re.compile("([1-9][0-9]*)$")
    num_nodes= raw_input("No. of nodes: ")
    
    while not(numnodes_pattern.match(num_nodes)):
    	num_nodes=raw_input("Enter valid no. of nodes: ")
    
    topo = SingleSwitchTopo(int(num_nodes))
    net = Mininet(topo)
    net.start()	
    
    for h in net.hosts:
	h.cmd("xterm -hold -e sudo python /home/ayush/Desktop/nodes.py "+num_nodes+" &")
    
    print "Testing network connectivity"
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
