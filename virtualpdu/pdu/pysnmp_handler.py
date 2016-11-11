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

import logging
import threading

from pyasn1.codec.ber import decoder
from pyasn1.codec.ber import encoder
from pysnmp.carrier.asyncore.dgram import udp
from pysnmp.carrier.asyncore.dispatch import AsyncoreDispatcher
from pysnmp.proto import api

# NOTE(mmitchell): Roughly from implementing-scalar-mib-objects.py in pysnmp.
# Unfortunately, that file is not part of the pysnmp package and re-use is
# not possible.
# pysnmp is distributed under the BSD license.

from virtualpdu.pdu import TraversableOidMapping


class SNMPPDUHandler(object):
    def __init__(self, pdu, community):
        self.pdu = pdu
        self.community = community
        self.logger = logging.getLogger(__name__)

    def message_handler(self, transportDispatcher, transportDomain,
                        transportAddress, whole_message):
        while whole_message:
            message_version = api.decodeMessageVersion(whole_message)
            if message_version in api.protoModules:
                protocol = api.protoModules[message_version]
            else:
                self.logger.warn(
                    'Unsupported SNMP version "{}"'.format(message_version))
                return

            request, whole_message = decoder.decode(
                whole_message, asn1Spec=protocol.Message()
            )

            response = protocol.apiMessage.getResponse(request)
            request_pdus = protocol.apiMessage.getPDU(request)
            community = protocol.apiMessage.getCommunity(request)

            if not self.valid_community(community):
                self.logger.warn('Invalid community "{}"'.format(community))
                return

            response_pdus = protocol.apiMessage.getPDU(response)
            var_binds = []
            pending_errors = []
            error_index = 0

            if request_pdus.isSameTypeWith(protocol.GetRequestPDU()):
                for oid, val in protocol.apiPDU.getVarBinds(request_pdus):
                    if oid in self.pdu.oid_mapping:
                        var_binds.append(
                            (oid, self.pdu.oid_mapping[oid].value))
                    else:
                        return
            elif request_pdus.isSameTypeWith(protocol.GetNextRequestPDU()):
                for oid, val in protocol.apiPDU.getVarBinds(request_pdus):
                    error_index += 1
                    try:
                        oid = TraversableOidMapping(self.pdu.oid_mapping)\
                            .next(to=oid)
                        val = self.pdu.oid_mapping[oid].value
                    except (KeyError, IndexError):
                        pending_errors.append(
                            (protocol.apiPDU.setNoSuchInstanceError,
                             error_index)
                        )
                    var_binds.append((oid, val))
            elif request_pdus.isSameTypeWith(protocol.SetRequestPDU()):
                for oid, val in protocol.apiPDU.getVarBinds(request_pdus):
                    error_index += 1
                    if oid in self.pdu.oid_mapping:
                        self.pdu.oid_mapping[oid].value = val
                        var_binds.append((oid, val))
                    else:
                        var_binds.append((oid, val))
                        pending_errors.append(
                            (protocol.apiPDU.setNoSuchInstanceError,
                             error_index)
                        )
            else:
                protocol.apiPDU.setErrorStatus(response_pdus, 'genErr')

            protocol.apiPDU.setVarBinds(response_pdus, var_binds)

            # Commit possible error indices to response PDU
            for f, i in pending_errors:
                f(response_pdus, i)

            transportDispatcher.sendMessage(
                encoder.encode(response), transportDomain, transportAddress
            )

        return whole_message

    def valid_community(self, community):
        return str(community) == self.community


class SNMPPDUHarness(threading.Thread):
    def __init__(self, pdu, listen_address, listen_port, community="public"):
        super(SNMPPDUHarness, self).__init__()
        self.logger = logging.getLogger(__name__)

        self.pdu = pdu

        self.snmp_handler = SNMPPDUHandler(self.pdu, community=community)

        self.listen_address = listen_address
        self.listen_port = listen_port
        self.transportDispatcher = AsyncoreDispatcher()

        self._lock = threading.Lock()
        self._stop_requested = False

    def run(self):
        with self._lock:
            if self._stop_requested:
                return

            self.logger.info("Starting PDU '{}' on {}:{}".format(
                self.pdu.name, self.listen_address, self.listen_port)
            )
            self.transportDispatcher.registerRecvCbFun(
                self.snmp_handler.message_handler)

            # UDP/IPv4
            self.transportDispatcher.registerTransport(
                udp.domainName,
                udp.UdpSocketTransport().openServerMode(
                    (self.listen_address, self.listen_port))
            )

            self.transportDispatcher.jobStarted(1)

        try:
            # Dispatcher will never finish as job#1 never reaches zero
            self.transportDispatcher.runDispatcher()
        except Exception:
            self.transportDispatcher.closeDispatcher()

    def stop(self):
        with self._lock:
            self._stop_requested = True
            try:
                self.transportDispatcher.jobFinished(1)
            except KeyError:
                pass  # The job is not started yet and will not start
