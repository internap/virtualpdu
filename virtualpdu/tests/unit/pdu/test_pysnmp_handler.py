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

import mock
from mock import sentinel
from pysnmp.carrier.asyncore.dgram import udp
from virtualpdu.pdu import pysnmp_handler
from virtualpdu.tests import base


class TestSNMPPDUHarness(base.TestCase):

    @mock.patch('virtualpdu.pdu.pysnmp_handler.udp.UdpSocketTransport')
    @mock.patch('virtualpdu.pdu.pysnmp_handler.SNMPPDUHandler')
    @mock.patch('virtualpdu.pdu.pysnmp_handler.AsyncoreDispatcher')
    def test_harness_thread_is_dispatched_correctly(
            self, asyncore_dispatcher_mock, snmp_pdu_handler_mock, udp_mock):

        udp_mock.return_value = mock.Mock()
        snmp_pdu_handler_mock2 = mock.Mock()
        snmp_pdu_handler_mock2.message_handler = sentinel.message_handler
        snmp_pdu_handler_mock.return_value = snmp_pdu_handler_mock2
        transport_dispatcher_mock = mock.Mock()
        asyncore_dispatcher_mock.return_value = transport_dispatcher_mock
        udp_mock.return_value = mock.Mock()
        udp_mock.return_value.openServerMode.return_value = sentinel.data

        harness = pysnmp_handler.SNMPPDUHarness(sentinel.pdu,
                                                sentinel.listen_address,
                                                sentinel.listen_port,
                                                sentinel.community)

        harness.start()

        snmp_pdu_handler_mock.assert_called_with(
            sentinel.pdu, community=sentinel.community
        )
        transport_dispatcher_mock.registerRecvCbFun.assert_called_with(
            sentinel.message_handler
        )
        udp_mock.return_value.openServerMode.assert_called_with(
            (sentinel.listen_address, sentinel.listen_port)
        )
        transport_dispatcher_mock.registerTransport.assert_called_with(
            udp.domainName, sentinel.data
        )
        transport_dispatcher_mock.jobStarted.assert_called_with(1)
        transport_dispatcher_mock.runDispatcher.assert_called_with()

        harness.stop()

    @mock.patch('virtualpdu.pdu.pysnmp_handler.udp.UdpSocketTransport')
    @mock.patch('virtualpdu.pdu.pysnmp_handler.SNMPPDUHandler')
    @mock.patch('virtualpdu.pdu.pysnmp_handler.AsyncoreDispatcher')
    def test_harness_dispatcher_closed_when_running_dispatcher_raises(
            self, asyncore_dispatcher_mock, snmp_pdu_handler_mock, udp_mock):

        udp_mock.return_value = mock.Mock()
        snmp_pdu_handler_mock2 = mock.Mock()
        snmp_pdu_handler_mock2.message_handler = sentinel.message_handler
        snmp_pdu_handler_mock.return_value = snmp_pdu_handler_mock2
        transport_dispatcher_mock = mock.Mock()
        asyncore_dispatcher_mock.return_value = transport_dispatcher_mock
        udp_mock.return_value = mock.Mock()
        udp_mock.return_value.openServerMode.return_value = sentinel.data
        transport_dispatcher_mock.runDispatcher.side_effect = Exception()

        harness = pysnmp_handler.SNMPPDUHarness(sentinel.pdu,
                                                sentinel.listen_address,
                                                sentinel.listen_port,
                                                sentinel.community)

        harness.start()

        snmp_pdu_handler_mock.assert_called_with(
            sentinel.pdu, community=sentinel.community
        )
        transport_dispatcher_mock.registerRecvCbFun.assert_called_with(
            sentinel.message_handler
        )
        udp_mock.return_value.openServerMode.assert_called_with(
            (sentinel.listen_address, sentinel.listen_port)
        )
        transport_dispatcher_mock.registerTransport.assert_called_with(
            udp.domainName, sentinel.data
        )
        transport_dispatcher_mock.jobStarted.assert_called_with(1)
        transport_dispatcher_mock.closeDispatcher.assert_called_with()

        harness.stop()


class TestPySNMPHandler(base.TestCase):
    pass
