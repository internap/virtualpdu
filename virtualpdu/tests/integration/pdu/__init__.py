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

import random
import threading

from mock import mock
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.entity.rfc3413.oneliner import cmdgen
from virtualpdu.pdu.pysnmp_handler import SNMPPDUHandler
from virtualpdu.tests import base
from virtualpdu.tests import snmp_client


class PDUTestCase(base.TestCase):
    pdu_class = NotImplementedError

    def setUp(self):
        super(PDUTestCase, self).setUp()

        self.community = 'test1212'
        self.core_mock = mock.Mock()
        self.pdu = self.pdu_class(name='test_pdu', core=self.core_mock)
        self.pdu_test_harness = SNMPPDUTestHarness(self.pdu,
                                                   None,
                                                   None,
                                                   self.community)
        self.pdu_test_harness.start()

    def tearDown(self):
        self.pdu_test_harness.stop()
        super(PDUTestCase, self).tearDown()

    def snmp_get(self, oid, community=None):
        s = snmp_client.SnmpClient(cmdgen,
                                   self.pdu_test_harness.listen_address,
                                   self.pdu_test_harness.listen_port,
                                   community or self.community,
                                   timeout=1,
                                   retries=1)
        return s.get_one(oid)

    def snmp_set(self, oid, value, community=None):
        s = snmp_client.SnmpClient(cmdgen,
                                   self.pdu_test_harness.listen_address,
                                   self.pdu_test_harness.listen_port,
                                   community or self.community,
                                   timeout=1,
                                   retries=1)

        return s.set(oid, value)


class SNMPPDUTestHarness(threading.Thread):
    def __init__(self, pdu, listen_address, listen_port, community="public"):
        super(SNMPPDUTestHarness, self).__init__()
        self.pdu = pdu

        self.snmp_handler = SNMPPDUHandler(self.pdu, community=community)

        self.listen_address = listen_address or '127.0.0.1'
        # TODO(mmitchell): bind port "0" and let OS decide of a port.
        # requires communicating back with parent thread to inform of port
        # number *OR* open socket and pass it to the thread.
        self.listen_port = listen_port or random.randint(20000, 30000)
        self.community = community
        self.transportDispatcher = AsyncoreDispatcher()

    def run(self):
        self.transportDispatcher.registerRecvCbFun(
            self.snmp_handler.message_handler)

        # UDP/IPv4
        self.transportDispatcher.registerTransport(
            udp.domainName, udp.UdpSocketTransport().openServerMode(
                (self.listen_address, self.listen_port))
        )

        self.transportDispatcher.jobStarted(1)

        try:
            # Dispatcher will never finish as job#1 never reaches zero
            self.transportDispatcher.runDispatcher()
        except Exception:
            self.transportDispatcher.closeDispatcher()
            raise

    def stop(self):
        self.transportDispatcher.jobFinished(1)
