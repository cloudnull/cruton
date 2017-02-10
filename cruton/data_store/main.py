# Copyright 2017, Rackspace US, Inc.
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

# (c) 2017, Kevin Carter <kevin.carter@rackspace.com>

import os
import pkgutil

from oslo_config import cfg

import cruton
import cruton.data_store.drivers as drivers


CONF = cfg.CONF


def add_command_parsers(subparsers):
    """Data store management commands.

    :param subparsers: parser object
    :type subparsers: object || class
    """

    subparsers.add_parser(
        'sync_tables',
        help="Sync the DB Tables."
    )


def main():
    """Main data store management entry point."""

    pkgpath = os.path.dirname(drivers.__file__)
    for _, name, _ in pkgutil.iter_modules([pkgpath]):
        cruton.dynamic_import(path='cruton.data_store.drivers.%s' % name)

    # Set the scheme management environment variable required
    os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = 'true'

    command_opt = cfg.SubCommandOpt(
        'command',
        title='Command',
        help='Available commands',
        handler=add_command_parsers
    )

    CONF.register_cli_opt(command_opt)
    CONF(project='cruton')

    data_store = CONF['data_store']
    data_connection_setup = cruton.dynamic_import(
        path='cruton.data_store.drivers.%s.utils' % data_store['driver'],
        module='setup'
    )
    if data_connection_setup:
        data_connection_setup()

    sync_data_store_cmd = cruton.dynamic_import(
        path='cruton.data_store.drivers.%s.models' % data_store['driver'],
        module='sync_tables'
    )
    sync_data_store_cmd(keyspace=[data_store['keyspace']])
