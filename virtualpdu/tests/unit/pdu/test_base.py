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

from mock import mock
from virtualpdu.pdu import PDU
from virtualpdu.power_states import POWER_OFF
from virtualpdu.tests import base


class TestPDU(base.TestCase):
    def setUp(self):
        super(TestPDU, self).setUp()
        self.core_mock = mock.Mock()
        self.pdu = PDU(name='my_pdu', core=self.core_mock)

    def test_power_off_notifies_core(self):
        self.pdu.oids[0].value = 'off'
        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            name='my_pdu',
            outlet_number=1,
            state=POWER_OFF)
