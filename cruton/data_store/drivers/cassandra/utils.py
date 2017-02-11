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

import cassandra
from cassandra.cqlengine import connection
from cassandra.auth import PlainTextAuthProvider

from oslo_config import cfg
from oslo_log import log as logging

import models


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class Exceptions(object):
    """General exceptions class.

    This class puulls in the execptions from the driver in a method allowing
    it to be universally accessed.
    """
    InvalidRequest = cassandra.InvalidRequest


def _auth_provider(conf):
    """Return an authentication object."""
    username = conf.get('username')
    password = conf.get('password')
    if username and password:
        return PlainTextAuthProvider(
            username=conf['username'],
            password=conf['password']
        )


def close(conn):
    """Close any open Session."""
    conn.shutdown()


def setup():
    """Run the connection setup."""
    cassandra_conf = CONF['data_store']
    cluster_connect = dict(
        hosts=cassandra_conf['cluster_node'],
        port=cassandra_conf['port'],
        default_keyspace=cassandra_conf['keyspace'],
        executor_threads=6,
        retry_connect=True,
        lazy_connect=True
    )
    auth_provider = _auth_provider(conf=cassandra_conf)
    if auth_provider:
        cluster_connect['auth_provider'] = auth_provider
    connection.setup(**cluster_connect)
    return connection


def _search(self, q, search_dict):
    """Search query results."""
    all_list = [dict(i.items()) for i in q.all()]
    if not any([i['opt'] for i in search_dict.values()]):
        return [self._friendly_return(i) for i in all_list]

    q_list = list()
    for item in all_list:
        for k, v in self.query.items():
            query_str = item.get(k)
            if query_str and v in query_str:
                q_list.append(self._friendly_return(item))
                continue

        fuzzy = search_dict['fuzzy']['opt']
        for k, v in search_dict.items():
            if v['parent'] and v['opt']:
                criteria = item.get(v['parent'], None)
                if criteria:
                    if isinstance(criteria, dict):
                        criteria = criteria.keys()
                    elif isinstance(criteria, set):
                        criteria = list(criteria)

                    criteria = [i.lower() for i in criteria]
                    if fuzzy:
                        criteria = ' '.join(criteria)

                    if v['opt'].lower() in criteria:
                        q_list.append(self._friendly_return(item))
    else:
        return q_list


def _get_search(self, model, ent_id=None, env_id=None, dev_id=None):
    """Retrieve a list of entities.

    :param self: Class object
    :type self: object || query
    :param model: DB Model object
    :type model: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param dev_id: Device ID
    :type dev_id: string
    :return: list
    """

    # This creates a single use search criteria hash which is used to look
    #  inside a list or other hashable type.
    search_dict = {
        'fuzzy': {
            'opt': self.query.pop('fuzzy', False),
            'parent': None
        },
        'tag': {
            'opt': self.query.pop('tag', None),
            'parent': 'tags'
        },
        'access_ip': {
            'opt': self.query.pop('access_ip', None),
            'parent': 'access_ip'
        },
        'port': {
            'opt': self.query.pop('port', None),
            'parent': 'ports'
        },
        'var': {
            'opt': self.query.pop('var', None),
            'parent': 'vars'
        },
        'link': {
            'opt': self.query.pop('link', None),
            'parent': 'links'
        },
        'contact': {
            'opt': self.query.pop('contact', None),
            'parent': 'contacts'
        }
    }

    lookup_params = dict()
    if ent_id:
        lookup_params['ent_id'] = ent_id
    if env_id:
        lookup_params['env_id'] = env_id
    if dev_id:
        lookup_params['dev_id'] = dev_id

    try:
        if dev_id:
            return [model.objects(**lookup_params).get()]
        elif search_dict['fuzzy']['opt']:
            q = model.objects.filter(**lookup_params).allow_filtering()
        else:
            lookup_params.update(self.query)
            q = model.objects.filter(**lookup_params).allow_filtering()
    except model.DoesNotExist as exp:
        LOG.error(str(exp))
        return list()
    else:
        return _search(
            self=self,
            q=q,
            search_dict=search_dict
        )


def get_device(self, ent_id, env_id, dev_id=None):
    """Retrieve a list of entities.

    :param self: Class object
    :type self: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param dev_id: Device ID
    :type dev_id: string
    :return: list
    """
    return _get_search(
        self=self,
        model=models.Devices,
        ent_id=ent_id,
        env_id=env_id,
        dev_id=dev_id
    )


def get_environment(self, ent_id, env_id=None):
    """Retrieve a list of entities.

    :param self: Class object
    :type self: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :return: list
    """
    return _get_search(
        self=self,
        model=models.Environments,
        ent_id=ent_id,
        env_id=env_id
    )


def get_entity(self, ent_id):
    """Retrieve a list of entities.

    :param self: Class object
    :type self: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :return: list
    """
    return _get_search(
        self=self,
        model=models.Environments,
        ent_id=ent_id
    )


def _put_item(args, query, ent_id=None, env_id=None, dev_id=None, update=False):
    """PUT an item.

    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param dev_id: Device ID
    :type dev_id: string
    :param args: Dictionary arguments
    :type args: dict
    :return: dict
    """
    args['updated_at'] = datetime.datetime.utcnow()
    if update:
        query.update(**args)
    else:
        args['created_at'] = args['updated_at']
        if ent_id:
            args['ent_id'] = ent_id
        if env_id:
            args['env_id'] = env_id
        if dev_id:
            args['dev_id'] = dev_id
        models.Devices.objects.limit(1).create(**args)
    return args


def _update_tags(query, args, model_exception):
    """Coalesce tags

    :param query: Class object
    :type query: object || query
    :param args: Dictionary arguments
    :type args: dict
    :param model_exception: Class object
    :type model_exception: exception
    :return:
    """
    try:
        r_dev = query.get()
        args['tags'] = set(list(r_dev['tags']) + list(args.pop('tags', list())))
    except model_exception:
        return args, False
    else:
        return args, True


def _put_links(end_q, endpoint, end_id, args):
    """PUT Links back.

    :param end_q: Class object
    :type end_q: object || query
    :param endpoint: Environment ID
    :type endpoint: string
    :param end_id: Entity ID
    :type end_id: string
    :param args: Dictionary arguments
    :type args: dict
    """
    # Post back a link within the entity to the new environment
    links = end_q.get()['links']
    if not links:
        links = dict()

    if endpoint.endswith(end_id):
        links[end_id] = endpoint
    else:
        links[end_id] = '%s/%s' % (endpoint, end_id)

    end_q.update(**{'links': links, 'updated_at': args['updated_at']})


def put_device(self, ent_id, env_id, dev_id, args):
    """PUT an entity.

    :param self: Class object
    :type self: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param dev_id: Device ID
    :type dev_id: string
    :param args: Dictionary arguments
    :type args: dict
    :return: string, int
    """
    try:
        q_env = models.Environments.objects(
            ent_id=ent_id,
            env_id=env_id
        ).limit(1)
    except models.Environments.DoesNotExist:
        return {'ERROR': 'Environment %s does not exist' % env_id}, 400

    q_dev = models.Devices.objects(
        env_id=env_id,
        ent_id=ent_id,
        dev_id=dev_id
    ).limit(1)

    args, update = _update_tags(
        query=q_dev,
        args=args,
        model_exception=models.Devices.DoesNotExist
    )

    try:
        # Write data to the backend
        args = _put_item(
            args=args,
            query=q_dev,
            ent_id=ent_id,
            env_id=env_id,
            dev_id=dev_id,
            update=update
        )

        _put_links(
            end_q=q_env,
            endpoint=self.endpoint,
            end_id=dev_id,
            args=args
        )
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200


def put_environment(self, ent_id, env_id, args):
    """PUT an entity.

    :param self: Class object
    :type self: object || query
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param args: Dictionary arguments
    :type args: dict
    :return: string, int
    """
    try:
        q_ent = models.Environments.objects(
            ent_id=ent_id,
            env_id=env_id
        ).limit(1)
    except models.Environments.DoesNotExist:
        return {'ERROR': 'Entity %s does not exist' % ent_id}, 400

    q_env = models.Environments.objects(
        env_id=env_id,
        ent_id=ent_id
    ).limit(1)

    args, update = _update_tags(
        query=q_env,
        args=args,
        model_exception=models.Devices.DoesNotExist
    )

    try:
        # Write data to the backend
        args = _put_item(
            args=args,
            query=q_env,
            ent_id=ent_id,
            env_id=env_id,
            update=update
        )

        _put_links(
            end_q=q_ent,
            endpoint=self.endpoint,
            end_id=env_id,
            args=args
        )
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200


def put_entity(self, ent_id, args):
    """PUT an entity.

    :param self: object
    :param ent_id: Entity ID
    :type ent_id: string
    :param args: Dictionary arguments
    :type ent_id: dict
    :return: string, int
    """
    q_ent = models.Entities.objects(
        ent_id=ent_id
    ).limit(1)

    args, update = _update_tags(
        query=q_ent,
        args=args,
        model_exception=models.Devices.DoesNotExist
    )

    try:
        # Write data to the backend
        args = _put_item(
            args=args,
            query=q_ent,
            ent_id=q_ent,
            update=update
        )
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200
