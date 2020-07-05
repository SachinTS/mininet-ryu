#!/usr/bin/python

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from sys import argv

def build_switch(net, sw=None, sw_str=None):
    sw.cmdPrint('bash experiment/start_ovsdb.sh ' + sw_str)
    sw.cmdPrint('bash experiment/start_ovs.sh ' + sw_str)
    sw.cmdPrint('bash experiment/create_sdn.sh ' + sw_str)

def ovsns(number_of_hosts=2):

    "Create an empty network and add nodes to it."

    net = Mininet( topo=None,
                   build=False)

    # setup initial topology. run ovs inside each host s1 and s2
    hr = net.addHost( 'hr', ip='10.0.0.90' )
    s1 = net.addHost( 's1', ip='0.0.0.0' )
    s2 = net.addHost( 's2', ip='0.0.0.0' )
    hc = net.addHost( 'hc', ip='10.0.0.95' )
    net.addLink( hr, s1 )
    net.addLink( hc, s1 )
    net.addLink( s1, s2 )

    hosts = list()
    #  add all remaining hosts to s2
    info( '*** Adding hosts and Links\n')

    for i in range (1,number_of_hosts+1):
        name = 'h'+str(i)
        host = net.addHost(name)
        # Add the link between s2 and  the host
        bandWidth = random.randint(200, 400)
        net.addLink(s2,host,bw=bandWidth,delay=2)
        hosts.append(host)

    #  start mininet topology
    info( '*** Starting network\n')
    net.start()
    # start controller in hc
    hc.cmdPrint('ryu-manager /usr/local/lib/python3.4/dist-packages/ryu/app/simple_switch_13.py \
                --verobose 1>/tmp/controller-ryu.log 2>&1 &')
    # setup ovs switches in s1 and s2
    info('** creating switches\n')
    build_switch(net, s1, 's1')
    build_switch(net, s2, 's2')
    s1.cmdPrint('ifconfig s1 inet 10.0.0.100/8')
    s2.cmdPrint('ifconfig s2 inet 10.0.0.101/8')

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    ovsns(int(argv[1]))
