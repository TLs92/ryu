from ryu.app import simple_switch_13
from ryu.ofproto import ofproto_v1_3
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER


class Mymonitor13(simple_switch_13.SimpleSwitch13):
    '''this is a simple monitor'''

    def __init__(self, *args, **kwargs):
        super(Mymonitor13, self).__init__(*args, **kwargs)

    # get datapath info
    @set_ev_cls(ofp_event.EventOFPPortStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        pass

    #send stats request message to datapath.
    def _request_stats(self, datapath):
        pass

    #handle the port stats reply msg.
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        pass

    #handle the flow entry stats reply msg.
    @set_ev_cls(ofp_event.OFPPortFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        pass