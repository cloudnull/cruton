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

from flask import jsonify, make_response, request
from flask_restful import reqparse

from cruton.api import v1 as v1_api
from cruton.api.v1 import entity


PARSER = reqparse.RequestParser()


class BaseEnvironments(entity.BaseEntity):
    def __init__(self):
        """TODO"""
        super(BaseEnvironments, self).__init__()
        self.model = self.models.Environments
        self._load_opts()

    def _get(self, ent_id=None, env_id=None, **kwargs):
        """Common GET method.

        :param ent_id: Entity ID
        :type ent_id: string
        :param ent_id: Environment ID
        :type ent_id: string
        :return: list
        """
        return self.utils.get_environment(
            self=self, ent_id=ent_id, env_id=env_id, **kwargs
        )

    def _put(self, ent_id=None, env_id=None, **kwargs):
        """Common PUT method.

        :param ent_id: Entity ID
        :type ent_id: string
        :param ent_id: Environment ID
        :type ent_id: string
        :return: string, int
        """
        return self.utils.put_environment(
            self=self, ent_id=ent_id, env_id=env_id, **kwargs
        )


class Environments(v1_api.ApiSkelRoot, BaseEnvironments):
    """Specific environment endpoint."""

    def __init__(self):
        super(Environments, self).__init__()

    def get(self, ent_id):
        try:
            return jsonify(self._get(ent_id=ent_id))
        except Exception as exp:
            return make_response(jsonify(str(exp)), 400)

    def head(self, ent_id):
        resp = make_response()
        resp.headers['Content-Environments'] = len(self._get(ent_id=ent_id))
        return resp

    def post(self, ent_id):
        if not isinstance(request.json, list):
            item_list = [request.json]
        else:
            item_list = request.json

        returns = list()
        for item in item_list:
            if not item:
                continue
            env_id = item.pop('env_id', None)
            if not env_id:
                return make_response(
                    '<env_id> is missing from the POST', 400
                )
            else:
                notice, code = self._put(ent_id=ent_id, env_id=env_id, args=item)
                if code >= 300:
                    return notice, code
                else:
                    returns.append(notice)
        else:
            return returns, 201


class Environment(v1_api.ApiSkelPath, BaseEnvironments):
    """Specific environment endpoint."""

    def __init__(self):
        super(Environment, self).__init__()
        self._env_id = None

    @property
    def env_id(self):
        """Datacenter Identification

        :param dc_id: Datacenter ID
        :type dc_id: string
        """
        return self._env_id

    def get(self, ent_id, env_id):
        try:
            return jsonify(
                self._friendly_return(
                    self._get(ent_id=ent_id, env_id=env_id)[0]
                )
            )
        except self.exp.InvalidRequest:
            return make_response(jsonify('DoesNotExist'), 404)
        except Exception as exp:
            return make_response(jsonify(str(exp)), 400)

    def head(self, ent_id, env_id):
        resp = make_response()
        resp.headers['Content-Environment-Exists'] = len(self._get(ent_id=ent_id, env_id=env_id)) > 0
        return resp

    def put(self, ent_id, env_id):
        notice, code = self._put(ent_id=ent_id, env_id=env_id, args=self.args)
        if code >= 300:
            return notice, code
        else:
            return notice, 201
