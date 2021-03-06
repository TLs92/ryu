# Copyright (C) 2013 Nippon Telegraph and Telephone Corporation.
# Copyright (C) 2013 YAMAMOTO Takashi <yamamoto at valinux co jp>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# convenient classes to manipulate OF-Config XML
# in a little more pythonic way.
# currently assuming OF-Config 1.1.1.

from ryu.lib import stringify


from .base import _Base, _ct, _e, _ns_netconf
from .generated_classes import *


# probably should not be here but for convenience
class NETCONF_Config(_Base):
    _ELEMENTS = [
        _ct('capable-switch', OFCapableSwitchType, is_list=False),
    ]

    def to_xml(self):
        return super(NETCONF_Config, self).to_xml('{%s}config' % _ns_netconf)
