# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from virtualpdu.tests import snmp_error_indications


class SnmpClient(object):
    def __init__(self, oneliner_cmdgen, host, port, community, timeout,
                 retries):
        self.host = host
        self.port = port
        self.community = community
        self.timeout = timeout
        self.retries = retries

        cmdgen = oneliner_cmdgen
        self.command_generator = cmdgen.CommandGenerator()
        self.community_data = cmdgen.CommunityData(self.community)
        self.transport = cmdgen.UdpTransportTarget((self.host, self.port),
                                                   timeout=self.timeout,
                                                   retries=self.retries)

    def get_one(self, oid):
        error_indication, error_status, error_index, var_binds = \
            self.command_generator.getCmd(self.community_data,
                                          self.transport,
                                          oid)

        self._handle_error_indication(error_indication)

        name, val = var_binds[0]
        return val

    def get_next(self, oid):
        error_indication, error_status, error_index, var_binds = \
            self.command_generator.nextCmd(self.community_data,
                                           self.transport,
                                           oid)

        self._handle_error_indication(error_indication)
        for varBindTableRow in var_binds:
            for name, val in varBindTableRow:
                return name, val

    def set(self, oid, value):
        error_indication, error_status, error_index, var_binds = \
            self.command_generator.setCmd(self.community_data,
                                          self.transport,
                                          (oid, value))

        self._handle_error_indication(error_indication)

        name, val = var_binds[0]
        return val

    def _handle_error_indication(self, error_indication):
        if error_indication:
            raise snmp_error_indications.__dict__.get(
                error_indication.__class__.__name__)()
