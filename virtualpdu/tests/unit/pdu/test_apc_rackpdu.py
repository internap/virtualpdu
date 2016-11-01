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
from pyasn1.type import univ
from virtualpdu.pdu import apc_rackpdu
from virtualpdu.pdu import sysDescr
from virtualpdu.pdu import sysObjectID
from virtualpdu.tests import base
from virtualpdu.tests.unit.pdu.base_pdu_test_cases import BasePDUTests


class TestAPCRackPDU(base.TestCase, BasePDUTests):
    pdu_class = apc_rackpdu.APCRackPDU
    outlet_control_oid = \
        apc_rackpdu.rPDU_outlet_control_outlet_command \
        + (apc_rackpdu.APCRackPDU.outlet_index_start,)
    outlet_name_oid = \
        apc_rackpdu.rPDU_outlet_config_outlet_name \
        + (apc_rackpdu.APCRackPDU.outlet_index_start,)

    def test_read_outlet_name(self):
        outlet_name = self.pdu.oid_mapping[self.outlet_name_oid]

        self.assertEqual(
            univ.OctetString('Outlet #1'),
            outlet_name.value
        )

    def test_read_system_description(self):
        self.assertEqual(
            univ.OctetString("APC Rack PDU (virtualpdu)"),
            self.pdu.oid_mapping[sysDescr].value
        )

    def test_read_system_oid(self):
        self.assertEqual(
            univ.ObjectIdentifier(apc_rackpdu.rPDU),
            self.pdu.oid_mapping[sysObjectID].value
        )
