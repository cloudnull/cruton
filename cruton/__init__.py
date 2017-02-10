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

import importlib

import pbr.version

from oslo_config import cfg


__version__ = pbr.version.VersionInfo('cruton').version_string()

# Api Options
OPS = [
    cfg.StrOpt('host', default="127.0.0.1", help="API host IP."),
    cfg.IntOpt('port', default=5150, help="API port to use."),
]

# Load config and API options
CONF = cfg.CONF
OPT_GROUP = cfg.OptGroup(
    name='api',
    title='Cruton API service group options.'
)
CONF.register_group(OPT_GROUP)
CONF.register_opts(OPS, OPT_GROUP)


# Api Options
DATA_OPS = [
    cfg.StrOpt(
        'driver',
        default="cassandra",
        help="Name of the keyspace to store data."
    ),
    cfg.StrOpt(
        'username',
        default="cruton",
        help="Username to connect to the cassandra cluster."
    ),
    cfg.StrOpt(
        'password',
        help="Password for user to connect to the cassandra cluster."
    ),
    cfg.MultiStrOpt(
        'cluster_node',
        default=["127.0.0.1"],
        help="Cluster IP address. This is can be used more than once."
    ),
    cfg.IntOpt(
        'port',
        default=9042,
        help="Cluster port number."
    ),
    cfg.StrOpt(
        'keyspace',
        default="cruton",
        help="Name of the keyspace to store data."
    )
]
DATA_OPS_GROUP = cfg.OptGroup(
    name='data_store',
    title='Cruton Data store group options.'
)
CONF.register_group(DATA_OPS_GROUP)
CONF.register_opts(DATA_OPS, DATA_OPS_GROUP)


def dynamic_import(path, module=None):
    """Import and Read a path with a given module if provided.

    :param path: Full path to import in "." notation.
    :type path: str
    :param module: Class name or method to import within a given path.
    :type module: str
    :rtype: import object
    """
    imp = importlib.import_module(path)
    if module:
        return getattr(imp, module)
    else:
        return imp
