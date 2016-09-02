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

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import sys

import virtualpdu.core
from virtualpdu.drivers import libvirt_driver
from virtualpdu.pdu import apc_rackpdu
from virtualpdu.pdu import pysnmp_handler

MISSING_CONFIG_MESSAGE = 'Missing configuration file as first parameter.\n'

logging.basicConfig(level=logging.DEBUG)


def main():
    try:
        config_file = sys.argv[1]
    except IndexError:
        sys.stderr.write(MISSING_CONFIG_MESSAGE)
        sys.exit(1)
    else:
        config = configparser.RawConfigParser()
        config.read(config_file)
        driver = get_driver_from_config(config)
        mapping = get_mapping_for_config(config)
        core = virtualpdu.core.Core(driver=driver, mapping=mapping)
        pdu_threads = []
        for pdu in [s for s in config.sections() if s != 'global']:

            apc_pdu = apc_rackpdu.APCRackPDU(pdu, core)

            listen_address = config.get(pdu, 'listen_host')
            port = int(config.get(pdu, 'listen_port'))
            community = config.get(pdu, 'community')

            pdu_threads.append(pysnmp_handler.SNMPPDUHarness(
                apc_pdu,
                listen_address,
                port,
                community
            ))

        for t in pdu_threads:
            t.start()

        try:
            for t in pdu_threads:
                while t.isAlive():
                    t.join(1)
        except KeyboardInterrupt:
            for t in pdu_threads:
                t.stop()
            sys.exit()


def get_driver_from_config(conf):
    try:
        uri = conf.get('global', 'libvirt_uri')
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        raise UnableToParseConfig(e)
    return libvirt_driver.LibvirtDriver(uri=uri)


def get_mapping_for_config(conf):
    sections = [s for s in conf.sections() if s != 'global']
    mapping = {}
    try:
        for pdu in sections:
            ports = conf.get(pdu, 'ports')
            list_of_ports = ports.split(',')
            for data in list_of_ports:
                port, host = data.split(':')
                mapping[(pdu, int(port))] = host
    except configparser.NoOptionError as e:
        raise UnableToParseConfig(e)
    return mapping


class UnableToParseConfig(Exception):
    pass
