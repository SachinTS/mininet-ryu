#!/usr/bin/python

from mininet.net import Mininet
from mininet.link import OVSLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from sys import argv

import subprocess
import random
from datetime import datetime

def build_switch(net, sw=None, sw_str=None):
    sw.cmdPrint('bash experiment/start_ovsdb.sh ' + sw_str)
    sw.cmdPrint('bash experiment/start_ovs.sh ' + sw_str)
    sw.cmdPrint('bash experiment/create_sdn.sh ' + sw_str)

def ovsns(number_of_hosts=2):

    "Create an empty network and add nodes to it."

    net = Mininet( topo=None,
                   build=False, link=OVSLink)

    # setup initial topology. run ovs inside each host s1 and s2
    hr = net.addHost( 'hr', ip='10.0.0.90' )
    s1 = net.addHost( 's1', ip='0.0.0.0' )
    s2 = net.addHost( 's2', ip='0.0.0.0' )
    hc = net.addHost( 'hc', ip='10.0.0.95' )

    # add required links
    net.addLink( hr, s1, delay=2)
    net.addLink( hc, s1 )
    net.addLink( s1, s2, bw=10000,delay=0.16 )

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
                --verbose 1>/tmp/controller-ryu.log 2>&1 &')
    # setup ovs switches in s1 and s2
    info('** creating switches\n')
    build_switch(net, s1, 's1')
    build_switch(net, s2, 's2')
    s1.cmdPrint('ifconfig s1 inet 10.0.0.100/8')
    s2.cmdPrint('ifconfig s2 inet 10.0.0.101/8')

    # iperfDuration = 20  #To speed-up testing, reduce the iperf duration (while developing your Ryu solution)
    cmd = 'iperf -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
    hr.cmd(cmd)

    for src in net.hosts:  # For each host in the network

        cmd = 'iperf -c ' + hr.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
        src.cmdPrint(cmd)   # Run the client (data source) on h1 to send data to host.IP
        cmd = 'ping -c 5000 -f ' + hr.IP() + ' >> /tmp/pinging'
        src.cmdPrint(cmd)
        # time = datetime.now()
        # info("** time   :")
        # info(str(time.minute) + ':' + str(time.second) + "\n")
        # time = datetime.now()
        net.pingAll()

        info("** time    :")
        info(str(time.minute) + ':' + str(time.second) + "\n")

    info('\n*** Wait ',str(iperfDuration), ' seconds for Iperf to Finish\n')
    # sleep(iperfDuration)
    CLI( net )
    net.stop()
    # cleanup switch processes
    subprocess.Popen("kill -9 `ps -ef | grep /tmp/mininet | grep -v grep | awk '{ print $2 }'`", shell=True, stdout=subprocess.PIPE).stdout.read()

if __name__ == '__main__':
    setLogLevel( 'info' )
    ovsns(int(argv[1]))
