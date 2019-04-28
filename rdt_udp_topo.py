### Used for rdt over UDP project
# to inject losses and delay
import sys
import time
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

linkOneGigDelayNoLoss = dict(bw = 1000, delay='5ms', loss=0, max_queue_size=1000, use_htb=True)
linkOneGigDelayLoss = dict(bw = 1000, delay='5ms', loss=5, max_queue_size=1000, use_htb=True)
linkOneGigNoDelayNoLoss = dict(bw = 1000, delay='0ms', loss=0, max_queue_size=1000, use_htb=True)

class SimpleTopo(Topo):
	"Two hosts connected through a switch"
	def build(self):
		switch1 = self.addSwitch('s1')
		host1 = self.addHost('h1')
#		self.addLink(host1, switch1, **linkOneGigNoDelayNoLoss)
		self.addLink(host1, switch1, **linkOneGigDelayLoss)

		host2 = self.addHost('h2')
#		self.addLink(host2, switch1, **linkOneGigNoDelayNoLoss)
		self.addLink(host2, switch1, **linkOneGigDelayLoss)


def perfTest():
	"Create network"
	topo = SimpleTopo()
	net = Mininet(topo=topo,
			 link=TCLink)
	net.start()
	print ("Dumping host connections")
	dumpNodeConnections(net.hosts)
	print ("Testing network connectivity")
	net.pingAll()
	c0, h1, h2 = net.get('c0','h1', 'h2')
	print ('c0.IP, h1.IP, h2.IP = ', c0.IP, h1.IP(), h2.IP())
	h1.cmd('python3 GBNrcvr_mininet.py -i %s > r.out &' %h1.IP())
        h2.cmd('python3 GBNsndr_mininet.py -i %s > s.out &' %h1.IP())
	print("IP address of h1 is %s" % h1.IP())
	print("IP address of h2 is %s" % h2.IP())
	
	CLI(net) #####
	net.stop()

if __name__ == '__main__':
	# tell mininet to print useful info
	setLogLevel('info')
	perfTest()

