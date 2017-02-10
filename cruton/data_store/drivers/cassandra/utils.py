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

import models


CONF = cfg.CONF


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


def _search(self, q, tag, contact=None, access_ip=None, ports=None, vars=None):
    """Search query results."""
    all_list = [dict(i.items()) for i in q.all()]
    if not self.query and not tag and not contact:
        return [self._friendly_return(i) for i in all_list]

    q_list = list()
    for item in all_list:
        for k, v in self.query.items():
            query_str = item.get(k)
            if query_str and v in query_str:
                q_list.append(self._friendly_return(item))
                continue

        # Run a tag search
        if tag and tag in item.get('tags', list()):
            q_list.append(self._friendly_return(item))

        # Run a contact search
        if contact and contact in item.get('contacts', dict()):
            q_list.append(self._friendly_return(item))

        # Run a access search
        if access_ip and access_ip in item.get('access_ip', dict()):
            q_list.append(self._friendly_return(item))

        # Run a port search
        if ports and ports in item.get('ports', dict()):
            q_list.append(self._friendly_return(item))

        # Run a port search
        if vars and vars in item.get('vars', dict()):
            q_list.append(self._friendly_return(item))
    else:
        return q_list


def _link_add(links, endpoint, end_id):
    if endpoint.endswith(end_id):
        links[end_id] = endpoint
    else:
        links[end_id] = '%s/%s' % (endpoint, end_id)
    return links


def _tags_add(new_tags, old_tags):
    return set(list(new_tags) + list(old_tags))


def put_device(self, ent_id, env_id, dev_id, args):
    """PUT an entity.

    :param self: object
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param args: Dictionary arguments
    :type ent_id: dict
    :param dev_id: Device ID
    :type dev_id: string
    :return: string, int
    """
    args['updated_at'] = datetime.datetime.utcnow()
    try:
        qe = models.Environments.objects(ent_id=ent_id, env_id=env_id)
        if qe.if_exists():
            q = models.Devices.objects(env_id=env_id, ent_id=ent_id, dev_id=dev_id)
            if q.if_exists():
                args['tags'] = _tags_add(old_tags=qe.get()['tags'], new_tags=args.pop('tags', list()))
                q.update(**args)
            else:
                args['created_at'] = args['updated_at']
                args['ent_id'] = ent_id
                args['env_id'] = env_id
                args['dev_id'] = dev_id
                models.Devices.objects.create(**args)
            # Post back a link within the entity to the new environment
            links = _link_add(links=qe.get()['links'], endpoint=self.endpoint, end_id=dev_id)
            if links:
                qe.update(**{'links': links})
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200


def get_device(self, ent_id, env_id, dev_id):
    """Retrieve a list of entities.

    :param self: object
    :param ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param dev_id: Device ID
    :type dev_id: string
    :return: list
    """
    fuzzy = self.query.pop('fuzzy', False)
    tag = self.query.pop('tag', None)
    access_ip = self.query.pop('access_ip', None)
    ports = self.query.pop('ports', None)
    vars = self.query.pop('vars', None)

    if dev_id:
        return [models.Devices.objects(ent_id=ent_id, env_id=env_id, dev_id=dev_id).get()]
    elif fuzzy:
        q = models.Devices.objects.filter(ent_id=ent_id, env_id=env_id).allow_filtering()
    else:
        q = models.Devices.objects.filter(ent_id=ent_id, env_id=env_id, **self.query).allow_filtering()

    return _search(self=self, q=q, tag=tag, access_ip=access_ip, ports=ports, vars=vars)


def put_environment(self, ent_id, env_id, args):
    """PUT an entity.

    :param self: object
    :param ent_id: Entity ID
    :type ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :param ent_id: Dictionary arguments
    :type ent_id: dict
    :return: string, int
    """
    args['updated_at'] = datetime.datetime.utcnow()
    try:
        qe = models.Entities.objects(ent_id=ent_id)
        if qe.if_exists():
            q = models.Environments.objects(env_id=env_id, ent_id=ent_id)
            if q.if_exists():
                args['tags'] = _tags_add(old_tags=qe.get()['tags'], new_tags=args.pop('tags', list()))
                q.update(**args)
            else:
                args['created_at'] = args['updated_at']
                args['ent_id'] = ent_id
                args['env_id'] = env_id
                models.Environments.objects.create(**args)
            # Post back a link within the entity to the new environment
            links = _link_add(links=qe.get()['links'], endpoint=self.endpoint, end_id=env_id)
            if links:
                qe.update(**{'links': links})
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200


def get_environment(self, ent_id, env_id=None):
    """Retrieve a list of entities.

    :param self: object
    :param ent_id: string
    :param env_id: Environment ID
    :type env_id: string
    :return: list
    """
    fuzzy = self.query.pop('fuzzy', False)
    tag = self.query.pop('tag', None)
    contact = self.query.pop('contact', None)
    vars = self.query.pop('vars', None)

    if env_id:
        return [models.Environments.objects(ent_id=ent_id, env_id=env_id).get()]
    elif fuzzy:
        q = models.Environments.objects.filter(ent_id=ent_id).allow_filtering()
    else:
        q = models.Environments.objects.filter(ent_id=ent_id, **self.query).allow_filtering()

    return _search(self=self, q=q, tag=tag, contact=contact, vars=vars)


def put_entity(self, ent_id, args):
    """PUT an entity.

    :param self: object
    :param ent_id: Entity ID
    :type ent_id: string
    :param args: Dictionary arguments
    :type ent_id: dict
    :return: string, int
    """
    args['updated_at'] = datetime.datetime.utcnow()
    try:
        q = models.Entities.objects(ent_id=ent_id).limit(None)
        if q.if_exists():
            args['tags'] = _tags_add(old_tags=q.get()['tags'], new_tags=args.pop('tags', list()))
            q.update(**args)
        else:
            args['created_at'] = args['updated_at']
            args['ent_id'] = ent_id
            models.Entities.objects.create(**args)
    except Exception as exp:
        return {'ERROR': str(exp)}, 400
    else:
        return self._friendly_return(args), 200


def get_entity(self, ent_id):
    """Retrieve a list of entities.

    :param self: object
    :param ent_id: string
    :return: list
    """
    fuzzy = self.query.pop('fuzzy', False)
    tag = self.query.pop('tag', None)
    contact = self.query.pop('contact', None)

    if ent_id:
        return [models.Entities.objects(ent_id=ent_id).get()]
    elif fuzzy:
        q = models.Entities.objects.filter()
    else:
        q = models.Entities.objects.filter(**self.query)

    return _search(self=self, q=q, tag=tag, contact=contact)
