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

import datetime
import collections

from flask import jsonify, make_response, request
from flask_restful import Resource

from oslo_config import cfg

import cruton
from cruton.main import APP


CONF = cfg.CONF
UTILS = cruton.dynamic_import(
    path='cruton.data_store.drivers.%s.utils' % CONF['data_store']['driver']
)
MODEL = cruton.dynamic_import(
    path='cruton.data_store.drivers.%s.models' % CONF['data_store']['driver']
)
QUERY = cruton.dynamic_import(
    path='cruton.data_store.drivers.%s' % CONF['data_store']['driver']
)


class ApiSkel(Resource):
    """Helper class for basic API skeleton."""
    def __init__(self):
        self.app = APP
        self.endpoint = request.path
        self.utils = UTILS
        self.conn = self.utils.setup()
        self.models = MODEL
        self.exp = self.utils.Exceptions
        self.model = None
        self.args = dict()
        self.query = dict()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.utils.close(conn=self.conn)  # Closes the connection to the data store

    def _load_opts(self):
        """Load available options based on items within the Models."""
        model_map = self.model.__model_map__
        if request.json:
            for k, v in model_map.items():
                if not isinstance(request.json, list):
                    arg = request.json.get(k)
                    if arg:
                        self.args[k] = v(arg)

        for k, v in request.args.items():
            self.query[k] = v
        self.query = self.convert(data=self.query)
        self.args = self.convert(data=self.args)

    def convert(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data

    def set_kwargs(self, kwargs):
        """Dynamically set objects into the class using the provided kwargs"""
        for k, v in kwargs.items():
            setattr(self, '_%s' % k, v)

    @staticmethod
    def _friendly_return(hashable):
        """Helper function to sanitize information before it's returned.

        :param hashable: dictionary
        :return: ``dict``
        """
        sanitized = dict()
        for key, value in hashable.items():
            if isinstance(value, set):
                value = list(value)
            elif isinstance(value, datetime.datetime):
                value = value.strftime('%d-%m-%Y %H:%M:%S')
            sanitized[key] = value
        else:
            return sanitized

    def _get(self, *args, **kwargs):
        pass

    def _put(self, *args, **kwargs):
        pass

    def get(self, **kwargs):
        """Default GET method. Returns 501 and arguments presented"""
        self.set_kwargs(kwargs=kwargs)
        return make_response(jsonify(kwargs), 501)

    def head(self, **kwargs):
        """Default HEAD method. Returns 501 and arguments presented"""
        self.set_kwargs(kwargs=kwargs)
        return make_response(jsonify(kwargs), 501)


class ApiSkelRoot(ApiSkel):
    """Helper class for basic API skeleton at a document root."""
    def __init__(self):
        super(ApiSkelRoot, self).__init__()

    def post(self, **kwargs):
        """Default POST method. Returns 501 and arguments presented"""
        self.set_kwargs(kwargs=kwargs)
        return make_response(501)


class ApiSkelPath(ApiSkel):
    """Helper class for basic API skeleton at a document path."""
    def __init__(self):
        super(ApiSkelPath, self).__init__()

    def put(self, **kwargs):
        """Default PUT method. Returns 501 and arguments presented"""
        self.set_kwargs(kwargs=kwargs)
        return make_response(jsonify(kwargs), 501)

    def delete(self, **kwargs):
        """Default DELETE method. Returns 501 and arguments presented"""
        self.set_kwargs(kwargs=kwargs)
        return make_response(jsonify(kwargs), 501)
