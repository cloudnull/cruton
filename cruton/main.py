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


def main(debug=False):
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
        CONF(project='cruton')
        APP.run(debug=debug, **CONF['api'])


def debug():
    main(debug=True)


if __name__ == '__main__':
    debug()
