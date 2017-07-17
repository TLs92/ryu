from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3

class Hub(app_manager.RyuApp):
    """docstring for Hub"""


    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Hub, self).__init__(*args, **kwargs)
        self.addcount = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        print('ev   ',type(ev))
        # install the table-miss flow entry.
        match = ofp_parser.OFPMatch()
        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        print ('switch_features')
        print('datapath.id:',datapath.id)
        print('ev.msg.datapath_id:',ev.msg.datapath_id)
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        self.addcount = self.addcount+1
        # construct flow_mod message and send it.
        inst = [ofp_parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                            actions)]
        mod = ofp_parser.OFPFlowMod(datapath=datapath, priority=priority,
                               match=match, instructions=inst)

        print('addcount=',self.addcount)
        print(type(datapath))
        print ('addflow  id is: ', datapath.id,"  ")
        print (inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        actions = [ofp_parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        print('FLOOD')
        match = ofp_parser.OFPMatch()

        # install flow_mod to avoid packet_in next time.
        self.add_flow(datapath, 1, match, actions)
        print('packetin')

        out = ofp_parser.OFPPacketOut(
            datapath=datapath,buffer_id=msg.buffer_id,in_port=in_port,
            actions=actions)
        datapath.send_msg(out)

