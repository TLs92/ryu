from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, arp
from ryu.topology import event
from ryu.topology.api import get_switch,get_link
import networkx as nx


class shortest_forwarding(app_manager.RyuApp):
    '''description'''

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(shortest_forwarding, self).__init__(*args, **kwargs)
        self.network = nx.DiGraph()
        self.topology_api_app = self
        self.paths = {}

    # handle switch features info.
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_hander(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # install the table-miss flow entry
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                              ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


    def add_flow(self, datapath, priority, match, actions):
        # add a flow entry and install it into datapath.
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # construct a flow_mod msg and send it to datapath
        inst = [ofp_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                 actions)]
        mod = ofp_parser.OFPFlowMod(datapath = datapath, priority = priority,
                                    match = match, instructions = inst)

        datapath.send_msg(mod)


    # get topology and save it into networkx object
    @set_ev_cls(event.EventSwitchEnter, [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def get_topology(self, ev):
        # get nodes.
        switch_list = get_switch(self.topology_api_app, None)
        switches = [switch.dp.id for switch in switch_list]
        self.network.add_nodes_from(switches)

        # get links.
        link_list = get_link(self.topology_api_app, None)
        links = [(link.src.dpid, link.dst.dpid, {'port': link.src.port_no}) for link in link_list]
        self.network.add_edges_from(links)

        # reverse links
        links = [(link.dst.dpid, link.src.dpid, {'port': link.dst.port_no}) for link in link_list]
        self.network.add_edges_from(links)

    # calculate the out_port(get out port by using networkx's Dijkstra algorithm)
    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id

        # add links between host and access switch
        if src not in self.network:
            self.network.add_node(src)
            self.network.add_edge(dpid, src, {'port':in_port}) # from switch to host
            self.network.add_edge(src,dpid)                    # from host to switch
            self.paths.setdefault(src, {})
                # example:   self.paths.setdefault(src, {{dst:[1, 2, 3, 4]}, {dst1:[1, 2, 3, 4]}})

        # search dst's shortest path.
        if dst in self.network:
            # if path is not existed, calculate it and save it.
            if dst not in self.paths[src]:
                path = nx.shortest_path(self.network, src, dst)
                self.paths[src][dst] = path

            # find out_port to next hop.
            path = self.paths[src][dst]
            print("path:",path)
            next_hop = path[path.index(dpid)+1]
            out_port = self.network[dpid][next_hop]['port']

        else:
            out_port = datapath.ofproto.OFPP_FLOOD

        return out_port



    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        # get topology info.
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

            # parser and analyze the received packets.
        pkt = packet.Packet(msg.data)

            # analyze ethernet info.
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src
        in_port = msg.match['in_port']

        # get out_port (shortest path info).
        out_port = self.get_out_port(datapath, src, dst, in_port)
        actions = [ofp_parser.OFPActionOutput(out_port)]

        # install flow entries.
        if out_port != ofproto.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

             # send a packet out
        out = ofp_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions)
        datapath.send_msg(out)











