#!/usr/bin/python

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from sys import argv
from time import sleep
import subprocess
import random
from datetime import datetime


def tcpdump(host=None, interface='any'):
    cmd = 'tcpdump -s 0 -i '+ interface+' icmp -w /tmp/'+ interface +'.pcap &'
    host.cmdPrint(cmd)

def build_switch(net, sw=None, sw_str=None):
    sw.cmdPrint('bash experiment/start_ovsdb.sh ' + sw_str)
    sw.cmdPrint('bash experiment/start_ovs.sh ' + sw_str)
    sw.cmdPrint('bash experiment/create_sdn.sh ' + sw_str)

def test_network(hr, hd, net, hosts ):
    iperfDuration = 20  #To speed-up testing, reduce the iperf duration (while developing your Ryu solution)

    # hr.cmdPrint(cmd)

    # net.pingAll()
    sleep(2)
    l = len(hosts)
    for i,src in enumerate(hosts):  # For each host in the network

        if i != 1 :
            cmd = 'iperf -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
            src.cmdPrint(cmd)
            cmd = 'iperf -c ' + src.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
            hr.cmdPrint(cmd)
            # Run the client (data source) on h1 to send data to host.IP
            # time = datetime.now()
            # info("** time   :")
            # info(str(time.minute) + ':' + str(time.second) + "\n")
            time = datetime.now()
            info("** time    :")
            info(str(time.minute) + ':' + str(time.second) + "\n")
            # net.pingAll()
        if i == (l - l/2):
            # tcpdump(src)
            sleep(5)
            cmd = 'ping -c 20 ' + hd.IP() + ' >> /tmp/pinging &'
            src.cmdPrint(cmd)
    sleep(3)
    cmd = 'iperf -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
    hosts[1].cmdPrint(cmd)

    cmd = 'iperf -c ' + hosts[1].IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client1 &'
    # cmd = 'ping -c 3 ' + hr.IP() + ' >> /tmp/pinging &'
    hd.cmdPrint(cmd)


    info("** time    :")
    info(str(time.minute) + ':' + str(time.second) + "\n")

    info('\n*** Wait ',str(iperfDuration), ' seconds for Iperf to Finish\n')
    sleep(iperfDuration)

def setup_queue(s1, s2):
    # set up queues

    s1.cmdPrint('ovs-vsctl --db=unix:/tmp/mininet-s1/db.sock -- set port s1-eth2 qos=@newqos \
                        -- --id=@newqos create qos type=linux-htb queues:7=@OFQueue \
                        -- --id=@OFQueue create queue \
                        other-config:max-rate=1000000000 other-config:min-rate=300000000 other-config:priority=0')

    s1.cmdPrint('ovs-vsctl --db=unix:/tmp/mininet-s1/db.sock set port s1-eth3 qos=@newqos1 \
                        -- --id=@newqos1 create qos type=linux-htb queues:7=@OFQueue1 \
                        -- --id=@OFQueue1 create queue \
                        other-config:max-rate=1000000000 other-config:min-rate=300000000 other-config:priority=0')

    s2.cmdPrint('ovs-vsctl --db=unix:/tmp/mininet-s1/db.sock -- set port s1-eth1 qos=@newqos \
                        -- --id=@newqos create qos type=linux-htb queues:7=@OFQueue \
                        -- --id=@OFQueue create queue \
                        other-config:max-rate=1000000000 other-config:min-rate=300000000 other-config:priority=0')

    s2.cmdPrint('ovs-vsctl --db=unix:/tmp/mininet-s2/db.sock set port s2-eth0 qos=@newqos1 \
                        -- --id=@newqos1 create qos type=linux-htb queues:7=@OFQueue1 \
                        -- --id=@OFQueue1 create queue \
                        other-config:max-rate=1000000000 other-config:min-rate=300000000 other-config:priority=0')

    s2.cmdPrint('ovs-vsctl --db=unix:/tmp/mininet-s2/db.sock set port s2-eth2 qos=@newqos2 \
                        -- --id=@newqos2 create qos type=linux-htb queues:7=@OFQueue2 \
                        -- --id=@OFQueue2 create queue \
                        other-config:max-rate=1000000000 other-config:min-rate=300000000 other-config:priority=0')

def add_flows(s1, s2):
    s2.cmdPrint('ovs-ofctl add-flow s2 priority=65535,icmp,nw_dst=10.0.0.96,actions=set_queue:7,normal \
                 -O OpenFlow13')
    s2.cmdPrint('ovs-ofctl add-flow s2 priority=65535,icmp,nw_src=10.0.0.96,actions=set_queue:7,normal \
                 -O OpenFlow13')

    s1.cmdPrint('ovs-ofctl add-flow s1 priority=65535,icmp,nw_dst=10.0.0.96,actions=set_queue:7,normal \
                 -O OpenFlow13')
    s1.cmdPrint('ovs-ofctl add-flow s1 priority=65535,icmp,nw_src=10.0.0.96,actions=set_queue:7,normal \
                 -O OpenFlow13')

def ovsns(number_of_hosts=2):

    "Create an empty network and add nodes to it."

    net = Mininet( topo=None,
                   build=False, link=TCLink)

    # setup initial topology. run ovs inside each host s1 and s2
    hr = net.addHost( 'hr', ip='10.0.0.90' )
    s1 = net.addHost( 's1', ip='0.0.0.0' )
    s2 = net.addHost( 's2', ip='0.0.0.0' )
    hc = net.addHost( 'hc', ip='10.0.0.95' )
    hd = net.addHost( 'hd', ip='10.0.0.96' )

    # add required links
    net.addLink( hr, s1 )
    net.addLink( hc, s1 )
    net.addLink( hd, s1 )
    net.addLink( s1, s2 )

    hosts = list()
    #  add all remaining hosts to s2
    info( '*** Adding hosts and Links\n')

    for i in range (1,number_of_hosts+1):
        name = 'h'+str(i)
        host = net.addHost(name)
        # Add the link between s2 and  the host
        bandWidth = random.randint(700, 900)
        # net.addLink(s2,host,params1={'bw': 800, 'delay':2}, params2={'bw': 100, 'delay':2})
        net.addLink( s2, host )
        hosts.append(host)
    #  start mininet topology
    info( '*** Starting network\n')
    net.start()
    # start controller in hc
    hc.cmdPrint('ryu-manager /home/mininet/mininet-ryu/ryu/l4_switch.py \
                --verbose 1>/tmp/controller-ryu.log 2>&1 &')
    # setup ovs switches in s1 and s2
    info('** creating switches\n')

    build_switch(net, s1, 's1')
    build_switch(net, s2, 's2')

    s1.cmdPrint('ifconfig s1 inet 10.0.0.100/8')
    s2.cmdPrint('ifconfig s2 inet 10.0.0.101/8')
    # net.pingAll()
    setup_queue(s1, s2) # set up queue
    add_flows(s1, s2)
    # tcpdump(host=s2,interface='s2')
    # tcpdump(host=s1,interface='s1')
    l = len(hosts)
    tcpdump(host=hd,interface='hd-eth0')
    tcpdump(host=hosts[l - l/2])
    hosts[l - l/2].cmdPrint("ping -c 1 10.0.0.96" )
    #
    sleep(3)
    test_network(hr, hd, net, hosts)

    CLI( net )
    net.stop()
    # cleanup switch processes
    subprocess.Popen("kill -9 `ps -ef | grep /tmp/mininet | grep -v grep | awk '{ print $2 }'`",
                      shell=True, stdout=subprocess.PIPE).stdout.read()

if __name__ == '__main__':
    setLogLevel( 'info' )
    ovsns(int(argv[1]))
