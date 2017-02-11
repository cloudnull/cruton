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

from oslo_config import cfg

from cruton.api import v1 as v1_api


CONF = cfg.CONF
PARSER = reqparse.RequestParser(bundle_errors=True)


class BaseEntity(v1_api.ApiSkel):
    """Base class for entities."""

    def __init__(self):
        super(BaseEntity, self).__init__()
        self._ent_id = None
        self.model = self.models.Entities
        self._load_opts()

    @property
    def ent_id(self):
        """Datacenter Identification

        :param ent_id: Entity ID
        :type ent_id: string
        """
        return self._ent_id

    def _get(self, ent_id=None, **kwargs):
        """Common GET method.

        :param ent_id: Entity ID
        :type ent_id: string
        :return: list
        """
        return self.utils.get_entity(
            self=self, ent_id=ent_id, **kwargs
        )

    def _put(self, ent_id=None, **kwargs):
        """Common PUT method.

        :param ent_id: Entity ID
        :type ent_id: string
        :param args: Dictionary arguments
        :type ent_id: dict
        :return: string, int
        """
        return self.utils.put_entity(
            self=self, ent_id=ent_id, **kwargs
        )


class Entities(v1_api.ApiSkelRoot, BaseEntity):
    """Specific environment and datacenter endpoint."""

    def __init__(self):
        super(Entities, self).__init__()

    def get(self):
        """GET entities.

        All entities will be returned by this method.

        :return: Response || object
        """
        try:
            return jsonify(self._get())
        except Exception as exp:
            return make_response(jsonify(str(exp)), 400)

    def head(self):
        """HEAD entities.

        A response will be returned containing headers with the current
        entity count.

        :return: Response || object
        """
        resp = make_response()
        resp.headers['Content-Entities'] = len(self._get())
        return resp

    def post(self):
        """POST entities.

        A status code of 201 will along with notice data regarding the
        POST will be returned.

        :return: tuple
        """
        if not isinstance(request.json, list):
            item_list = [request.json]
        else:
            item_list = request.json

        returns = list()
        for item in item_list:
            if not item:
                continue
            ent_id = item.pop('ent_id', None)
            if not ent_id:
                return make_response(
                    '<ent_id> is missing from the POST', 400
                )
            else:
                notice, code = self._put(ent_id=ent_id, args=item)
                if code >= 300:
                    return notice, code
                else:
                    returns.append(notice)
        else:
            return returns, 201


class Entity(v1_api.ApiSkelPath, BaseEntity):
    """Specific environment and datacenter endpoint."""

    def __init__(self):
        super(Entity, self).__init__()

    def get(self, ent_id):
        """GET Entity.

        A response will be returned containing headers with the current
        entity count.

        :param ent_id: Entity ID
        :type ent_id: string
        :return: Response || object
        """
        try:
            return jsonify(self._friendly_return(self._get(ent_id=ent_id)[0]))
        except self.exp.InvalidRequest:
            return make_response(jsonify('DoesNotExist'), 404)
        except Exception as exp:
            return make_response(jsonify(str(exp)), 400)

    def head(self, ent_id):
        """HEAD Entity.

        A response will be returned containing headers with the current
        entity count.

        :param ent_id: Entity ID
        :type ent_id: string
        :return: Response || object
        """
        resp = make_response()
        resp.headers['Content-Entity-Exists'] = len(self._get(ent_id=ent_id)) > 0
        return resp

    def put(self, ent_id):
        """PUT Entity.

        A response will be returned containing headers with the current
        entity count.

        :param ent_id: Entity ID
        :type ent_id: string
        :return: tuple
        """
        notice, code = self._put(ent_id=ent_id, args=self.args)
        if code >= 300:
            return notice, code
        else:
            return notice, 201
