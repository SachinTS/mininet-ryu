#!/usr/bin/python

import random
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, UserSwitch, OVSSwitch
from mininet.link import TCULink, Intf
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from sys import argv
from time import sleep

from datetime import datetime



def build_switch(net, sw=None, sw_str=None):
    print
    sw.cmdPrint('bash experiment/start_ovsdb.sh ' + sw_str)
    sw.cmdPrint('bash experiment/start_ovs.sh ' + sw_str)
    sw.cmdPrint('bash experiment/create_sdn1.sh ' + sw_str)
    #sw.cmdPrint('ovs-vsctl set Bridge ' + sw_str + ' protocols=OpenFlow13')
    return

def myNetwork(number_of_hosts=2):

    # Create an instance of Mininet class i.e. the network with default values
    # net = Mininet(controller=RemoteController,switch=OVSSwitch,link=TCULink,autoSetMacs=True)
    net = Mininet(topo=None, build=False)
    info( '*** Adding controller\n' )
    # c0 = net.addController('c0', controller=RemoteController, ip='192.168.1.5', port=6653)
    info( '*** Adding switches\n')
    # s1 = net.addSwitch('s1', protocols='OpenFlow13', cls=OVSSwitch)
    # s2 = net.addSwitch('s2', protocols='OpenFlow13', cls=OVSSwitch)
    # Intf('enp0s8', node=s1)
    s1 = net.addHost('s1')
    s2 = net.addHost('s2')
    net.addLink(s1,s2,bw=10000,delay=0.16)
    hc = net.addHost('hc', ip='10.0.0.1')
    #hc.cmdPrint('ryu-manager /usr/local/lib/python3.4/dist-packages/ryu/app/simple_switch_13.py --verbose --log-file /tmp/ryu.log 2>/dev/null 1>2  &')
    hc.cmdPrint('controller -v ptcp:6633 &')
    net.addLink(s2,hc,bw=10000)
    hr = net.addHost('hr')
    net.addLink(s2,hr, delay=2)
    hosts = []
    info( '*** Adding hosts and Links\n')
    time = datetime.now()
    info("** time  :")
    info(str(time.minute) + ':' + str(time.second))
    for i in range (1,number_of_hosts+1):
        name = 'h'+str(i)
        host = net.addHost(name)
        # Add the link between s1 and  the host
        bandWidth = random.randint(200, 400)
        net.addLink(s1,host,bw=bandWidth,delay=10)
        # host.cmdPrint('dhclient' + host.defaultIntf().name)
        hosts.append(host)
    info( '*** Starting network\n')
    net.start()
    info('** creating switches\n')
    build_switch(net, s1, 's1')
    build_switch(net, s2, 's2')
    s1.cmdPrint('ifconfig s1 inet 10.0.0.100/8')
    s2.cmdPrint('ifconfig s2 inet 10.0.0.101/8')



    # for host in hosts:
    #     host.cmdPrint('ping -c 3 ' + hr.IP() + ' | grep rtt')
    #
    # # iperfDuration = 20  #To speed-up testing, reduce the iperf duration (while developing your Ryu solution)
    # cmd = 'iperf -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
    # hr.cmd(cmd)

    # for dst in net.hosts:
    # for src in net.hosts:  # For each host in the network
    #
    #     cmd = 'iperf -c ' + hr.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
    #     src.cmdPrint(cmd)   # Run the client (data source) on h1 to send data to host.IP
    #     cmd = 'ping -c 5000 -f ' + hr.IP() + ' >> /tmp/pinging'
    #     src.cmdPrint(cmd)
    #     # time = datetime.now()
    #     # info("** time   :")
    #     # info(str(time.minute) + ':' + str(time.second) + "\n")
    #     # time = datetime.now()
    #     net.pingAll()
    #
    #     info("** time    :")
    #     info(str(time.minute) + ':' + str(time.second) + "\n")
    #
    # info('\n*** Wait ',str(iperfDuration), ' seconds for Iperf to Finish\n')
    # sleep(iperfDuration)

    CLI(net)
    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork(int(argv[1]))
