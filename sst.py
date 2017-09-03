#!/usr/bin/python                                                                            
                                                                                             
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from subprocess import call

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
    num_nodes=raw_input("No. of nodes: ")
    topo = SingleSwitchTopo(int(num_nodes))
    net = Mininet(topo)
    net.start()	
    print "here"
    for h in net.hosts:
	h.cmd("tabbed -c xterm -hold -e sudo python /home/ayush/Desktop/merge6.py "+num_nodes+" &")
    print "Testing network connectivity"
    CLI(net)
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
