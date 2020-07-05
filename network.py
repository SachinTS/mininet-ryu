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

def myNetwork(number_of_hosts=2):

    # Create an instance of Mininet class i.e. the network with default values
    net = Mininet(controller=RemoteController,switch=OVSSwitch,link=TCULink,autoSetMacs=True)

    info( '*** Adding controller\n' )
    c0 = net.addController('c0', controller=RemoteController, ip='192.168.1.5', port=6633)

    info( '*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    # Intf('enp0s8', node=s1)
    # sleep(5)
    net.addLink(s1,s2,bw=40000,delay=0.16)
    hr = net.addHost('hr')
    net.addLink(s2,hr)
    net.addLink(s2,c0)
    hosts = []
    info( '*** Adding hosts and Links\n')
    time = datetime.now()
    info("** time  :")
    info(str(time.minute) + ':' + str(time.second))
    for i in range (1,number_of_hosts+1):
        name = 'h'+str(i)
        # ip = '1.0.0.'+ str(i)
        # ip = '0.0.0.0'
        # Add the hosts with IP address
        host = net.addHost(name)
        # Add the link between s1 and  the host
        bandWidth = random.randint(200, 400)
        net.addLink(s1,host,bw=bandWidth,delay=10)
        # host.cmdPrint('dhclient' + host.defaultIntf().name)
        hosts.append(host)
    info( '*** Starting network\n')
    net.start()
    # Run a pingall test
    # for host in hosts:
    #     host.cmdPrint('dhclient '+host.defaultIntf().name)
    #     host.cmdPrint(' ifconfig| grep -i broadcast ')
    # time = datetime.now()
    # net.pingAll()
    # # time = datetime.now()
    # info("** time   :")
    # info(str(time.minute) + ':' + str(time.second) + "\n")

    iperfDuration = 20  #To speed-up testing, reduce the iperf duration (while developing your Ryu solution)
    # info ('*** Running Iperf Tests\n')
    # time = datetime.now()
    # info("** time   :")
    # info(str(time.minute) + ':' + str(time.second) + "\n")
    # # Get the instance of h1
    # h1 = net.get('h1')
    # for src in net.hosts:
    #     for dst in net.hosts:  # For each host in the network
    #         if src != dst:      # Except h1
    #             # Start an Iperf server (data sink) on host that reports every second.
    #             # Use & to run in background and avoid blocking cmd. Also save the reports to a log file.
    #             cmd = 'iperf -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
    #             dst.cmd(cmd)   # Send the command to the host
    #             info(src.name, ' <==>', dst)
    #             # sleep(1)    # Wait for a second to ensure that the iperf server is running
    #             cmd = 'iperf -c ' + dst.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
    #             time = datetime.now()
    #             info(cmd + '\n')
    #             src.cmd(cmd)   # Run the client (data source) on h1 to send data to host.IP
    #             cmd = ' ping -c 5000 -f ' + dst.IP() + ' >> /tmp/pinging &'
    #             info(cmd + '\n')
    #             src.cmd(cmd)
    #             # sleep(1)    # Wait for a second before starting the next host
    #             # time = datetime.now()
    #             info("** time   :")
    #             info(str(time.minute) + ':' + str(time.second) + "\n")
    #             # sleep(3)
    #     time = datetime.now()
    #     net.pingAll()

    #     info("** time    :")
    #     info(str(time.minute) + ':' + str(time.second) + "\n")

    # info('\n*** Wait ',str(iperfDuration), ' seconds for Iperf to Finish\n')
    # sleep(iperfDuration)

    CLI(net)
    # Stop the network
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork(int(argv[1]))
