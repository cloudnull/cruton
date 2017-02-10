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

import re

import cruton
import cruton.api as api
import cruton.api.v1 as v1_api


def split_docs(doc_string):
    if doc_string:
        return [i.strip() for i in doc_string.splitlines() if i.strip()]
    else:
        return list()


def locate_method(*args):
    return '.'.join(args)


class Discovery(v1_api.ApiSkel):
    """API Discovery Information"""

    def __init__(self):
        super(Discovery, self).__init__()
        self.rule_endpoint = None
        self._docs_ep = None
        self._docs_func = None

    def _inputs(self, rule, info):
        _raw_inputs = [i for i in rule.arguments if i != 'self']
        if not _raw_inputs:
            return
        inputs = info['inputs'] = dict()
        for _raw_input in _raw_inputs:
            input_info = inputs[_raw_input] = dict()
            _docs = getattr(self._docs_func, _raw_input)
            _input_docs_split = split_docs(_docs.__doc__)
            if not _input_docs_split:
                break
            input_info['documentation'] = _input_docs_split
            for item in _input_docs_split:
                if item.startswith(':type'):
                    input_info['type'] = re.sub(':', '', item).split()[-1]

    def get(self):
        routes = dict()
        for rule in self.app.url_map.iter_rules():
            self.rule_endpoint = rule.endpoint.capitalize()
            lower_rule = self.rule_endpoint.lower()
            if rule and (lower_rule != 'static' and lower_rule != 'docroot'):
                info = routes[rule.rule] = dict()
                info['methods'] = list(rule.methods)

                self._docs_ep = api.API_MAP[lower_rule]
                self._docs_func = cruton.dynamic_import(
                    path=self._docs_ep['path'],
                    module=self._docs_ep['module']
                )
                if not self._docs_func:
                    continue
                _docs = split_docs(doc_string=self._docs_func.__doc__)
                info['documentation'] = _docs
                self._inputs(rule=rule, info=info)
        else:
            return routes
