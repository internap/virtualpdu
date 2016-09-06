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
import subprocess

import sys

import signal
import threading

import time

import tempfile

import os
from pysnmp.entity.rfc3413.oneliner import cmdgen
from virtualpdu.pdu import apc_rackpdu
from virtualpdu.tests import base
from virtualpdu.tests import snmp_client

TEST_CONFIG = """[global]
libvirt_uri=test:///default

[my_pdu]
listen_address=127.0.0.1
listen_port=9998
community=public
ports=5:test

[my_second_pdu]
listen_address=127.0.0.1
listen_port=9997
community=public
ports=2:test
"""


class TestEntrypointIntegration(base.TestCase):
    def test_entry_point_works(self):
        p = subprocess.Popen([
            sys.executable, self._get_entrypoint_path('virtualpdu')],
            stderr=subprocess.PIPE
        )
        stdout, stderr = p.communicate()
        self.assertEqual(
            b'Missing configuration file as first parameter.\n',
            stderr)
        self.assertEqual(1, p.returncode)

    def test_config(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(bytearray(TEST_CONFIG, encoding='utf-8'))
            f.flush()
            try:
                p = subprocess.Popen([
                    sys.executable,
                    self._get_entrypoint_path('virtualpdu'),
                    f.name,
                ])

                self.turn_off_outlet(community='public',
                                     listen_address='127.0.0.1',
                                     outlet=5,
                                     port=9998)

                self.turn_off_outlet(community='public',
                                     listen_address='127.0.0.1',
                                     outlet=2,
                                     port=9997)
            finally:
                p.kill()

    def test_SIGINT_stops_the_process(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(bytearray(TEST_CONFIG, encoding='utf-8'))
            f.flush()
            try:
                p = subprocess.Popen([
                    sys.executable,
                    self._get_entrypoint_path('virtualpdu'),
                    f.name,
                ])

                self.assertIsNone(p.poll())
                p.send_signal(signal.SIGINT)
                time.sleep(0.1)  # NOTE(mmitchell): Give it 100ms to stop.
                self.assertIsNotNone(p.poll())
            finally:
                try:
                    p.kill()
                except OSError:
                    pass

    def test_pdu_names_ips_and_ports_are_shown_on_stderr(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write(bytearray(TEST_CONFIG, encoding='utf-8'))
            f.flush()
            try:
                p = subprocess.Popen([
                    sys.executable,
                    self._get_entrypoint_path('virtualpdu'),
                    f.name,
                ], stderr=subprocess.PIPE)

                t = threading.Timer(1, p.send_signal, [signal.SIGINT])
                t.start()
                stdout, stderr = p.communicate()
                t.join()

                self.assertIn(b'my_pdu', stderr)
                self.assertIn(b'127.0.0.1:9998', stderr)

                self.assertIn(b'my_second_pdu', stderr)
                self.assertIn(b'127.0.0.1:9997', stderr)
            finally:
                try:
                    p.kill()
                except OSError:
                    pass

    def turn_off_outlet(self, community, listen_address, outlet, port):
        outlet_oid = apc_rackpdu.rPDU_outlet_control_outlet_command + (outlet,)
        snmp_client_ = snmp_client.SnmpClient(cmdgen,
                                              listen_address,
                                              port,
                                              community,
                                              timeout=1,
                                              retries=1)
        snmp_client_.set(outlet_oid,
                         apc_rackpdu.rPDU_power_mappings['immediateOff'])

    def _get_entrypoint_path(self, entrypoint):
        return os.path.join(os.path.dirname(sys.executable), entrypoint)
