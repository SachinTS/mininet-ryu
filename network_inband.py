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


def tcpdump(host=None, interface=None):
    cmd = 'tcpdump -s 0 -i any -w /tmp/'+ interface +'.pcap &'
    host.cmdPrint(cmd)

def build_switch(net, sw=None, sw_str=None):
    sw.cmdPrint('bash experiment/start_ovsdb.sh ' + sw_str)
    sw.cmdPrint('bash experiment/start_ovs.sh ' + sw_str)
    sw.cmdPrint('bash experiment/create_sdn.sh ' + sw_str)

def test_network(hr, net, hosts ):
    iperfDuration = 20  #To speed-up testing, reduce the iperf duration (while developing your Ryu solution)

    # hr.cmdPrint(cmd)

    # net.pingAll()
    sleep(2)
    l = len(hosts)
    for i,src in enumerate(hosts):  # For each host in the network

        if i != (l - 1) :
            cmd = 'iperf -u -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
            src.cmdPrint(cmd)
            cmd = 'iperf -u -c ' + src.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
            hr.cmdPrint(cmd)
            # Run the client (data source) on h1 to send data to host.IP
            cmd = 'ping -c 5000 -f ' + hr.IP() + ' >> /tmp/pinging &'
            src.cmdPrint(cmd)
            # time = datetime.now()
            # info("** time   :")
            # info(str(time.minute) + ':' + str(time.second) + "\n")
            time = datetime.now()
            info("** time    :")
            info(str(time.minute) + ':' + str(time.second) + "\n")
            # net.pingAll()
    sleep(10)
    # cmd = 'iperf -u -s ' + '-t' + str(iperfDuration) + '  >> /tmp/iperf_server.log &'
    # hr.cmdPrint(cmd)
    # cmd = 'iperf -u -c ' + hr.IP() + ' -t '+ str(iperfDuration) +' >> /tmp/iperf_client &'
    cmd = 'ping -c 3 ' + hr.IP() + ' >> /tmp/pinging &'
    hosts[l - 1].cmdPrint(cmd)


    info("** time    :")
    info(str(time.minute) + ':' + str(time.second) + "\n")

    info('\n*** Wait ',str(iperfDuration), ' seconds for Iperf to Finish\n')
    sleep(iperfDuration)

def test_parallel_con(hr, hosts):
    hr.cmdPrint("cd /tmp; fallocate -l 1600M gentoo_root.img; python -m SimpleHTTPServer 8080 &")
    p = 1
    for host in hosts:
        host.cmdPrint('for i in {1..'+ str(p)+ '}; do cd /tmp; wget -b -O /dev/null http://10.0.0.90:8080/gentoo_root.img; done')

def ovsns(number_of_hosts=2):

    "Create an empty network and add nodes to it."

    net = Mininet( topo=None,
                   build=False, link=TCLink)

    # setup initial topology. run ovs inside each host s1 and s2
    hr = net.addHost( 'hr', ip='10.0.0.90' )
    s1 = net.addHost( 's1', ip='0.0.0.0' )
    s2 = net.addHost( 's2', ip='0.0.0.0' )
    hc = net.addHost( 'hc', ip='10.0.0.95' )

    # add required links
    net.addLink( hr, s1, delay=2)
    net.addLink( hc, s1 )
    net.addLink( s1, s2, bw=20000,delay=0.16 )

    hosts = list()
    #  add all remaining hosts to s2
    info( '*** Adding hosts and Links\n')

    for i in range (1,number_of_hosts+1):
        name = 'h'+str(i)
        host = net.addHost(name)
        # Add the link between s2 and  the host
        bandWidth = random.randint(700, 900)
        net.addLink(s2,host,params1={'bw': 400, 'delay':2}, params2={'bw': 100, 'delay':2})
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
    #
    # tcpdump(host=s2,interface='s2')
    # tcpdump(host=s1,interface='s1')
    # tcpdump(host=hc,interface='hc')

    # test_network(hr, net, hosts)
    net.pingAll()
    sleep(2) # sleep for the OF handshake
    test_parallel_con(hr, hosts)


    CLI( net )
    net.stop()
    # cleanup switch processes
    subprocess.Popen("kill -9 `ps -ef | grep /tmp/mininet | grep -v grep | awk '{ print $2 }'`", shell=True, stdout=subprocess.PIPE).stdout.read()
    subprocess.Popen("kill -9 `ps -ef | grep SimpleHTTPServer | grep -v grep | awk '{ print $2 }'`", shell=True, stdout=subprocess.PIPE).stdout.read()

if __name__ == '__main__':
    setLogLevel( 'info' )
    ovsns(int(argv[1]))
