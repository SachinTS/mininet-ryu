##

# This file is a solution to Coursework-2 (Learning Switch)

# You should adapt this (or adapt your own solution from week 14) for Coursework 3

##


from ryu.base import app_manager

from ryu.controller import ofp_event

from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER

from ryu.controller.handler import set_ev_cls

from ryu.ofproto import ofproto_v1_3

from ryu.ofproto.ofproto_v1_3_parser import OFPMatch

from ryu.lib.packet import packet

from ryu.lib.packet import ethernet

from ryu.lib.packet import arp

from ryu.lib.packet import tcp

from ryu.lib.packet import ether_types

from ryu.lib.packet import in_proto as inet

from ryu.lib import dpid as dpid_lib, hub


# Imports for the RESTful API

from webob import Response

from ryu.app.wsgi import ControllerBase, WSGIApplication, route

import json

class LearningSwitch(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):

        super(LearningSwitch, self).__init__(*args, **kwargs)

        # Create Mappings Table

        self.mac_to_port = {}

        self.tuple_list = []

        self.communication_per_host = {}


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        ''' Handle Configuration Changes '''

        datapath = ev.msg.datapath

        ofproto = datapath.ofproto

        parser = datapath.ofproto_parser

        match = parser.OFPMatch()

        actions = [parser.OFPActionOutput(
            ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        print("EVENT: Switch added || dpid: 0x%09x" % (datapath.id))

        self.add_flow(datapath, 0, match, actions)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        ''' Handle Packet In OpenFlow Events '''

        #self.logger.info("EVENT: PACKET IN")

        # Collect EVENT data

        # The message containing all the data needed from the openflow event
        msg = ev.msg

        # The switch (datapath) that the event came from
        datapath = ev.msg.datapath

        # OF Protocol lib to be used with the OF version on the switch
        ofproto = ev.msg.datapath.ofproto

        # OF Protocol Parser that matches the OpenFlow version on the switch
        parser = ev.msg.datapath.ofproto_parser

        # ID of the switch (datapath) that the event came from
        dpid = ev.msg.datapath.id

        # Collect packet data

        # The packet relating to the event (including all of its headers)
        pkt = packet.Packet(msg.data)

        # The port that the packet was recieved on the switch
        in_port = msg.match['in_port']

        # Build basic (L2) match

        match_dict = {}

        # Lowest layer header avaliable (ethernet)
        eth = pkt.protocols[0]

        # Add the input port into the match
        match_dict["in_port"] = in_port

        # Add ethernet type into the match
        match_dict["eth_type"] = eth.ethertype

        # Add source mc address into the match
        match_dict["eth_src"] = eth.src

        # Add destination mac address into the match
        match_dict["eth_dst"] = eth.dst

        current_in_port = None

        # Build Advanced (L4) Match

        if eth.ethertype == ether_types.ETH_TYPE_IP:

            # For IP

            # Get the next header in, that, as ethertype is IP here, next header is IP
            ip = pkt.protocols[1]

            match_dict["ip_proto"] = ip.proto

            match_dict["ipv4_src"] = ip.src

            match_dict["ipv4_dst"] = ip.dst

            if ip.proto == inet.IPPROTO_TCP:

                # For TCP

                nw = pkt.protocols[2]

                match_dict["tcp_src"] = nw.src_port

                match_dict["tcp_dst"] = nw.dst_port

                #self.logger.info("MATCH CREATED: TCP")

            elif ip.proto == inet.IPPROTO_UDP:

                # For UDP

                nw = pkt.protocols[2]

                match_dict["udp_src"] = nw.src_port

                match_dict["udp_dst"] = nw.dst_port

                self.logger.info("MATCH CREATED: UDP")

            elif ip.proto == inet.IPPROTO_ICMP:

                # For ICMP

                icmp = pkt.protocols[2]

                match_dict["icmpv4_type"] = icmp.type

                match_dict["icmpv4_code"] = icmp.code

                self.logger.info("MATCH CREATED: ICMP")

            else:

                self.logger.info("MISS: Ignoring IP Proto %x" % (ip.proto))

                return

        elif eth.ethertype == ether_types.ETH_TYPE_ARP:

            # For ARP

            # Get the next header in, that, as ethertype is ARP here, next header is ARP
            arp = pkt.protocols[1]

            match_dict["arp_sha"] = arp.src_mac

            match_dict["arp_tha"] = arp.dst_mac

            match_dict["arp_spa"] = arp.src_ip

            match_dict["arp_tpa"] = arp.dst_ip

            match_dict["arp_op"] = arp.opcode

            #self.logger.info("MATCH CREATED: ARP")

        else:

            #self.logger.info("MISS: Ignoring Ethernet Type %x"%(eth.ethertype))

            return

        # Little fix for the ryu match problem with incremental match building in OFv1_3

        # Rather than using append_fields, that does not apply ordering, we use kwargs

        match = parser.OFPMatch(**match_dict)

        # Add the mac address to port mapping to the dict

        # The outer dict represents a mapping of switches to their mappings

        # The inner dict represents a mapping of mac addresses to ports

        self.mac_to_port.setdefault(dpid, {})

        self.mac_to_port[dpid][eth.src] = in_port

        # If the dst mac address has a mapping in the table, the switch should send the packet out only via the port mapped

        # Else, just flood the packet to all ports

        if eth.dst in self.mac_to_port[dpid]:

            out_port = self.mac_to_port[dpid][eth.dst]

            #self.logger.info("PACKET OUT: Port %s", str(out_port))

        else:

            #self.logger.info("PACKET OUT: Flooding")

            out_port = ofproto.OFPP_FLOOD

        # The action of sending a packet out converted to the correct OpenFLow format

        actions = [parser.OFPActionOutput(out_port)]

        # Install the Flow-Mod

        if out_port != ofproto.OFPP_FLOOD:

            if dpid is not 2:

                self.add_flow(datapath, 1, match, actions)

        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:

            data = msg.data

        # Although a flow-mod may have been installed, we still need to send the packet that

        # triggered the event back out

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,

                                  in_port=in_port, actions=actions, data=data)

        datapath.send_msg(out)

        return

    def add_flow(self, datapath, priority, match, actions):

        ofproto = datapath.ofproto

        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,

                                match=match, instructions=inst)

        #self.logger.info("FLOW MOD: Written")

        datapath.send_msg(mod)
