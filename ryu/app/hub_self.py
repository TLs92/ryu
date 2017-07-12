#-*- coding: utf0-8 -*-
from ryu.base import app_manager
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER


class Hub(app_manager.RyuApp):
    """this is a virtual Hub """

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Hub, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofprotohub
        ofp_parser = datapath.ofproto_parser

        # install the table-miss flow entry
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,      # 发送端口
                                             ofproto.OFPCML_NO_BUFFER)]     # 不存

        self.add_flow(datapath, 0, match, actions)


    def add_flow(self, datapath, priority, match, actions):
        # add a flow entry and install it into datapath.
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # construct a flow_mod msg and send it
        inst = [ofp_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                                 actions)]
        mod = ofp_parser.OFPFlowMod(datapath = datapath, priority = priority,
                                    match = match, instructions = inst)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # construct a flow_entry
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]

        # install flow_mod to avoid packet_in next time.
        self.add_flow(datapath, 1, match, actions)

        out = ofp_parser.OFPPacketOut(
            datapath = datapath, buffer_id = msg.buffer_id, in_port = in_port,
            actions = actions)
        datapath.send_msg(out)
