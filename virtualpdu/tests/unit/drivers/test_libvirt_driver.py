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

import libvirt
from mock import mock
from virtualpdu.drivers import DeviceNotFound
from virtualpdu.drivers.libvirt_driver import LibvirtDriver
from virtualpdu.tests import base

DOMAIN_ALREADY_RUNNING = "internal error: Domain '%s' is already running"


@mock.patch('libvirt.open', autospec=True)
class TestLibvirtDriver(base.TestCase):
    def test_power_on(self, mock_open):
        domain_mock = mock.Mock()
        connection_mock = mock.Mock()
        connection_mock.lookupByName.return_value = domain_mock
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        driver.power_on('domainA')

        mock_open.assert_called_with('hello')
        connection_mock.lookupByName.assert_called_with('domainA')
        domain_mock.create.assert_called_with()
        connection_mock.close.assert_called_with()

    def test_power_off(self, mock_open):
        domain_mock = mock.Mock()
        connection_mock = mock.Mock()
        connection_mock.lookupByName.return_value = domain_mock
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        driver.power_off('domainA')

        mock_open.assert_called_with('hello')
        connection_mock.lookupByName.assert_called_with('domainA')
        domain_mock.destroy.assert_called_with()
        connection_mock.close.assert_called_with()

    def test_power_on_domain_not_found(self, mock_open):
        connection_mock = mock.Mock()
        connection_mock.lookupByName.side_effect = \
            libvirt.libvirtError('virDomainLookupByName() failed',
                                 conn=connection_mock)
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        self.assertRaises(DeviceNotFound, driver.power_on, 'domainA')

        connection_mock.close.assert_called_with()

    def test_power_off_domain_not_found(self, mock_open):
        connection_mock = mock.Mock()
        connection_mock.lookupByName.side_effect = \
            libvirt.libvirtError('virDomainLookupByName() failed',
                                 conn=connection_mock)
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        self.assertRaises(DeviceNotFound, driver.power_off, 'domainA')

        connection_mock.close.assert_called_with()

    def test_power_on_domain_already_running(self, mock_open):
        domain_name = 'domainA'

        domain_mock = mock.Mock()
        connection_mock = mock.Mock()
        connection_mock.lookupByName.return_value = domain_mock

        domain_mock.create.side_effect = \
            libvirt.libvirtError(DOMAIN_ALREADY_RUNNING.format(domain_name),
                                 conn=connection_mock)
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        driver.power_on(domain_name)

        connection_mock.close.assert_called_with()

    def test_power_on_generic_error_goes_through(self, mock_open):
        domain_mock = mock.Mock()
        connection_mock = mock.Mock()
        connection_mock.lookupByName.return_value = domain_mock

        domain_mock.create.side_effect = SpecificException()
        mock_open.return_value = connection_mock

        driver = LibvirtDriver(uri='hello')
        self.assertRaises(SpecificException, driver.power_on, 'domainA')

        connection_mock.close.assert_called_with()


class SpecificException(Exception):
    pass
