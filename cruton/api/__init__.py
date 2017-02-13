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

from flask import jsonify
from flask_restful import Resource


BASE_API_MAP = {
    'discovery': {
        'module': 'Discovery',
        'path': 'cruton.api.v1.discovery',
        'uri': '/discovery'
    }
}

V1_API_MAP = {
    'entity': {
        'module': 'Entity',
        'path': 'cruton.api.v1.entity',
        'uri': '/v1/entities/<ent_id>'
    },
    'entities': {
        'module': 'Entities',
        'path': 'cruton.api.v1.entity',
        'uri': '/v1/entities'
    },
    'environment': {
        'module': 'Environment',
        'path': 'cruton.api.v1.environment',
        'uri': '/v1/entities/<ent_id>/environments/<env_id>'
    },
    'environments': {
        'module': 'Environments',
        'path': 'cruton.api.v1.environment',
        'uri': '/v1/entities/<ent_id>/environments'
    },
    'device_ipxe': {
        'module': 'Ipxe',
        'path': 'cruton.api.v1.device',
        'uri': '/v1/entities/<ent_id>/environments/<env_id>/devices/<dev_id>/ipxe'
    },
    'device': {
        'module': 'Device',
        'path': 'cruton.api.v1.device',
        'uri': '/v1/entities/<ent_id>/environments/<env_id>/devices/<dev_id>'
    },
    'devices': {
        'module': 'Devices',
        'path': 'cruton.api.v1.device',
        'uri': '/v1/entities/<ent_id>/environments/<env_id>/devices'
    }
}

API_VERSIONS = [V1_API_MAP]
API_MAP = dict()
for api_map in [BASE_API_MAP] + API_VERSIONS:
    API_MAP.update(api_map)


class DocRoot(Resource):
    def __init__(self):
        self.info = {
            'links': sorted([v.get('uri') for k, v in V1_API_MAP.items()]),
            'methods': ['HEAD', 'OPTION', 'GET']
        }

    def get(self):
        return jsonify(self.info)
