from operator import attrgetter

import json

from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.lib import hub


class Mymonitor13(simple_switch_13.SimpleSwitch13):
    '''this is a simple monitor'''

    def __init__(self, *args, **kwargs):
        super(Mymonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        # a micro thread(coroutine) to run _monitor()
        # hub.spawn() use eventlet's green process

    # get datapath info
    # EventOFPPortStateChange is a function offered by Ryu structure,when datapath's state changes,
    # it will be triggered.
    # datapath's state turn to MAIN_DISPATCHER,means switch is  registered and been watched.
    # datapath's state turn to DEAD_DISPATCHER,means switch is un-registered.
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            # switch is online.
            if datapath.id not in self.datapaths:
                # record this datapath
                self.datapaths[datapath.id] = datapath
                self.logger.debug("Register datapath: %16x",datapath.id)

        elif ev.state == DEAD_DISPATCHER:
            # switch is offline.
            if datapath.id in self.datapaths:
                # delete this record and log it.
                del self.datapaths[datapath.id]
                self.logger.debug("Register datapath: %16x",datapath.id)

    # send request msg periodically.
    # use eventlet way in __init__ .
    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)
            # 5 seconds intervals for each.

    # send stats request message to datapath.
    def _request_stats(self, datapath):
        self.logger.debug("send stats request to datapath: 16%x",datapath.id)
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        # send port stats request msg.
        # OFPPortStatsRequest requests that the switch provide port-related statistical info.
        # can specify the desired port number.here, OFPP_ANY means all ports.
        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

        # sned flow stats request msg.
        # OFPFlowStatsRequest requests that the switch provide port-related statistical info related to flow entry.
        req = ofp_parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    #handle the port stats reply msg.
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath                port    '
                         'receive-pkts      receive-bytes    receive-errors '
                         'send-pkts         send-bytes       send-errors ')
        self.logger.info('----------------------------       -----------------'
                         '---------------   ---------------    ---------------'
                         '---------------   ---------------    ---------------')

        for stat in sorted(body, key = attrgetter('port_no')):
            self.logger.info("%16x %8x %8d %8d %8d %8d %8d %8d",
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)

    #handle the flow entry stats reply msg.
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        # body is an attribute in OFPFlowStatsReply(is a FlowStats' list),
        # and it's storage each flow-entry statical info.
        # here,use json to show what is in body
        self.logger.info('%s', json.dumps(ev.msg.to_jsondict(), ensure_ascii=True, indent=3,
                                         sort_keys=True))


        self.logger.info('datapath                    '
                         'in_port           eth-dst                '
                         'out_port          packets          bytes '
                         )
        self.logger.info('---------------------------- '
                         '---------------   ------------------------'
                         '---------------   ---------------    ---------------')

        for stat in sorted([flow for flow in body if flow.priority == 1], key = lambda flow :(flow.match['in_port'],
                                                                                              flow.match['eth_dst'])):
            self.logger.info("%16x %8x %8d %8d %8d %8d %8d %8d",
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port, stat.packet_count,
                             stat.byte_count)
