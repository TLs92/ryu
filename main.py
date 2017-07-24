import os



from ryu.base import app_manager


PATH = os.path.dirname(__file__)
PYTHON_PATH = os.path.split(os.path.realpath(__file__))[0]


class SDRouteS(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(SDRouteS, self).__init__(*args, **kwargs)




app_manager.require_app('ryu.app.ofctl_rest')           #to support rest_api
app_manager.require_app('ryu.app.myapp.mymonitor13')
app_manager.require_app('ryu.app.myapp.shortest_forwarding')
# app_manager.require_app('ryu.app.gui_topology_ddos.gui_topology_ddos')
# app_manager.require_app('topology_manage.ProxyArp')
# app_manager.require_app('host_manage.host_manage_main')
# app_manager.require_app('host_manage.HostTrack')
# app_manager.require_app('host_manage.HostDiscovery')
# app_manager.require_app('load_balance.load_balancer_main')
# app_manager.require_app('link_monitor.link_monitor_main')
# app_manager.require_app('route_manage.RouteManage')
# app_manager.require_app('topology_manage.TopologyManage')
# app_manager.require_app('fault_recovery.fault_recovery_main')
