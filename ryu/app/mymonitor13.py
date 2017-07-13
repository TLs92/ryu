from ryu.app import simple_switch_13
from ryu.ofproto import ofproto_v1_3
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

    # get datapath info
    @set_ev_cls(ofp_event.EventOFPPortStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_chan_handler(self, ev):
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
                # delete is record.
                del self.datapaths[datapath.id]
                self.logger.debug("Register datapath: %16x",datapath.id)

    #send request msg periodically.
    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(5)
            # 5 seconds intervals for each.

    #send stats request message to datapath.
    def _request_stats(self, datapath):
        self.logger.debug("send stats request to datapath: 16%x",datapath.id)
        ofproto = datapath.ofproto
        ofp_parser = datapath.ofp_parser

        #send port stats request msg.
        req = ofp_parser.OFPPortStatsRequest(datapath)
        datapath.send_msg(req)

        #sned flow stats request msg.
        req = ofp_parser.OFPFlowStatsRequest(datapath, 0, ofproto.OFPP_ANY)
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
