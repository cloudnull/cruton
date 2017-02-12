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

import uuid

import cassandra.cqlengine.models as cql


class CrutonBaseModel(cql.Model):
    __abstract__ = True

    __options__ = {
        'compaction': {
            'class': 'LeveledCompactionStrategy',
            'sstable_size_in_mb': '128',
        }
    }

    __model_map__ = {
        'name': str,
        'tags': set,
        'links': dict
    }

    id = cql.columns.UUID(index=True, default=uuid.uuid4)
    name = cql.columns.Text(index=True, required=True)
    created_at = cql.columns.DateTime()
    updated_at = cql.columns.DateTime()
    tags = cql.columns.Set(
        value_type=cql.columns.Text()
    )
    links = cql.columns.Map(
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )
    description = cql.columns.Text(default=None)


class Entities(CrutonBaseModel):
    CrutonBaseModel.__model_map__.update({
        'ent_id': str,
        'ent_contacts': dict
    })

    ent_id = cql.columns.Text(primary_key=True)
    contacts = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )


class Environments(CrutonBaseModel):
    CrutonBaseModel.__model_map__.update({
        'ent_id': str,
        'env_id': str,
        'env_contacts': dict,
        'vars': dict
    })

    env_id = cql.columns.Text(primary_key=True)
    ent_id = cql.columns.Text(primary_key=True)
    contacts = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )
    vars = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )


class Devices(CrutonBaseModel):
    CrutonBaseModel.__model_map__.update({
        'dev_id': str,
        'env_id': str,
        'ent_id': str,
        'row_id': str,
        'rack_id': str,
        'units': str,
        'asset_id': str,
        'access_ip': dict,
        'ports': dict,
        'vars': dict
    })

    dev_id = cql.columns.Text(primary_key=True)
    env_id = cql.columns.Text(primary_key=True)
    ent_id = cql.columns.Text(primary_key=True)
    row_id = cql.columns.Text(default=None)
    rack_id = cql.columns.Text(default=None)
    units = cql.columns.Integer(default=None)
    asset_id = cql.columns.Text(default=None)
    access_ip = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Inet()
    )
    ports = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )
    vars = cql.columns.Map(
        default=dict(),
        key_type=cql.columns.Text(),
        value_type=cql.columns.Text()
    )


def sync_tables(keyspace):
    from cassandra.cqlengine import management

    management.sync_table(
        model=Entities,
        keyspaces=keyspace
    )

    management.sync_table(
        model=Environments,
        keyspaces=keyspace
    )

    management.sync_table(
        model=Devices,
        keyspaces=keyspace
    )
