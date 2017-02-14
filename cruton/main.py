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

from flask import Flask
from flask_restful import Api

from oslo_log import log as logging
from oslo_config import cfg

import cruton
import cruton.api as api

CONF = cfg.CONF

# Register the flask application
APP = Flask(__name__)
APP.config.update(PROPAGATE_EXCEPTIONS=True)
API = Api(APP)
LOG = logging.getLogger(__name__)

DEFAULT_CONFIG_FILE = []
if os.path.exists('/etc/cruton/cruton.ini'):
    DEFAULT_CONFIG_FILE.append('/etc/cruton/cruton.ini')


def init_application():
    for k, v, in api.API_MAP.items():
        API.add_resource(
            cruton.dynamic_import(
                path=v['path'],
                module=v['module']
            ),
            v['uri']
        )
    else:
        API.add_resource(api.DocRoot, '/')
        logging.register_options(CONF)
        logging.setup(CONF, 'cruton-api')
        CONF(
            project='cruton',
            version=cruton.__version__,
            default_config_files=DEFAULT_CONFIG_FILE
        )
        APP.config.update(CONF['api'])
        return APP


def debug():
    return init_application().run(debug=True, **CONF['api'])


if __name__ == '__main__':
    debug()
