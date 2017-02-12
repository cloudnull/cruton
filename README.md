![Cruton](docs/pics/cruton-logo.jpg)

### Rebaked environmental device management system

Environmental device management system built for hundreds of entities, thousands environments, and millions of devices.

----

## Creating the **role** and **keyspace** where the tables will be created.

This system requires access to a cassandra backend

###### You can create access restrictions like so.

``` cql
CREATE ROLE IF NOT EXISTS cruton WITH PASSWORD = 'secrete' AND LOGIN = true ;
```

If you have the AllowAllAuthenticator backend enabled you better have a good reason, otherwise it's likely you're doing
it wrong. [See for more on setting up internal authentication](http://docs.datastax.com/en/archived/datastax_enterprise/4.0/datastax_enterprise/sec/secConfiguringInternalAuthentication.html#secConfiuringInternalAuthentication__secConfiuringInternalAuthentication)

###### Create the keyspace.

``` cql
CREATE KEYSPACE IF NOT EXISTS "cruton" WITH REPLICATION = {'class': 'NetworkTopologyStrategy', 'datacenter1': 1};
```

###### Grant ALL permissions to the use for the created keyspace

``` cql
GRANT ALL ON KEYSPACE cruton TO cruton;
```

----

## Development via Docker

You can just build the cruton docker container by running the following command.
``` bash
docker build -t cloudnull/cruton .
```

To sync tables example
``` bash
docker run -ti -v ${PWD}/example:/etc/cruton -p 5150:5150 cloudnull/cruton cruton-manage --config-file /etc/cruton/cruton.ini sync_tables
```

----

## Installation of Cruton.

Installing the base system requirements
``` bash
apt-get install -y python-dev build-essential
```

Installing the python source code.
``` bash
# Create a python virtual environment and activate the venv
virtualenv cruton
. cruton/bin/activate

# Install the python package.
pip install cruton

# You could also install this package using git
# pip install git+https://github.com/cloudnull/cruton
````

Once the package is installed create the configuration file for the API. The assumed location of this file will be ``/etc/cruton``.

``` ini
[DEFAULT]
driver = cassandra

[api]
host = 0.0.0.0
port = 5150

[data_store]
username = cruton
password = secrete
cluster_node = 127.0.0.1
port = 9042
```

----

## Synchronizing the table space with the backend store.

``` bash
cruton-manage --config-file /etc/cruton/cruton.ini sync_tables
```

----

### Data Model

The data model is broken up into a simple hierarchy allowing for effective tracking of resources. Everything in the data models can be used as search criteria.

The top level is an "Entity". Within an Entity basic data covering an "owner" is stored.

``` cql
CREATE TABLE cruton.entities (
    ent_id text PRIMARY KEY,
    contacts map<text, text>,
    created_at timestamp,
    description text,
    id uuid,
    links map<text, text>,
    name text,
    tags set<text>,
    updated_at timestamp
) WITH bloom_filter_fp_chance = 0.1
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.LeveledCompactionStrategy', 'sstable_size_in_mb': '128'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';
CREATE INDEX entities_id_idx ON cruton.entities (id);
CREATE INDEX entities_name_idx ON cruton.entities (name);
```

The next level is the Environments which contains general information about the environment which resources are will be deployed under.

``` cql
CREATE TABLE cruton.environments (
    env_id text,
    ent_id text,
    contacts map<text, text>,
    created_at timestamp,
    description text,
    id uuid,
    links map<text, text>,
    name text,
    tags set<text>,
    updated_at timestamp,
    vars map<text, text>,
    PRIMARY KEY (env_id, ent_id)
) WITH CLUSTERING ORDER BY (ent_id ASC)
    AND bloom_filter_fp_chance = 0.1
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.LeveledCompactionStrategy', 'sstable_size_in_mb': '128'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';
CREATE INDEX environments_id_idx ON cruton.environments (id);
CREATE INDEX environments_name_idx ON cruton.environments (name);
```

The final level is the Devices which contains everything that will be tracked.

``` cql
CREATE TABLE cruton.devices (
    dev_id text,
    env_id text,
    ent_id text,
    access_ip map<text, inet>,
    asset_id text,
    created_at timestamp,
    description text,
    id uuid,
    links map<text, text>,
    name text,
    ports map<text, text>,
    rack_id text,
    row_id text,
    tags set<text>,
    units int,
    updated_at timestamp,
    vars map<text, blob>,
    PRIMARY KEY (dev_id, env_id, ent_id)
) WITH CLUSTERING ORDER BY (env_id ASC, ent_id ASC)
    AND bloom_filter_fp_chance = 0.1
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.LeveledCompactionStrategy', 'sstable_size_in_mb': '128'}
    AND compression = {'chunk_length_in_kb': '64', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND crc_check_chance = 1.0
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99PERCENTILE';
CREATE INDEX devices_id_idx ON cruton.devices (id);
CREATE INDEX devices_name_idx ON cruton.devices (name);
```

----

## Working with the API.

To start the API it's recommended that you run the service behind a webserver like NGINX, Apache, using uWSGI, etc.
The typical API process can be envoked by running the ``cruton-api-wsgi --config-file /etc/cruton/cruton.ini`` command.
If you need or want to run the API in debug mode you can do so by invoking the ``cruton-api-debug --config-file /etc/cruton/cruton.ini``
command.


### Discovery
```bash
curl 'http://127.0.0.1:5150/dicovery'
```
The API endpoints and all available actions are discoverable. The dicovery endpoint allows the a user or an
application to discover all available actions for all available versions.

### Entities

###### HEAD all entities
```
curl --head 'http://127.0.0.1:5150/v1/entities'
```

###### PUT an entity
``` bash
curl -H 'Content-Type: application/json' -D - -XPUT 'http://127.0.0.1:5150/v1/entities/Solo1' -d '{"name": "TestEntitySolo"}'
```

###### HEAD an entities
```
curl --head 'http://127.0.0.1:5150/v1/entities/Solo1'
```

###### POST one or many entities (bulk import)
``` bash
curl -H 'Content-Type: application/json'  -D - -XPOST 'http://127.0.0.1:5150/v1/entities' -d '[{"ent_id": "Ent1", "tags": ["TestEntityTagOne"], "contacts": {"person1": "4155551212", "person2": "email@person2.example.com"}, "name": "TestEntityOne"}, {"ent_id": "Ent2", "tags": ["TestEntityTagOne", "TestEntityTagTwo"], "contacts": {"person2": "email@person2.example.com"}, "name": "TestEntityTwo"}]'
```

###### GET entities
``` bash
curl 'http://127.0.0.1:5150/v1/entities'
````

###### GET entities and search
``` bash
curl -D - 'http://127.0.0.1:5150/v1/entities?contact=person1'
```

###### GET entities and search doing a partial match using provided criteria
``` bash
curl -D - 'http://127.0.0.1:5150/v1/entities?name=EntityTag&fuzzy=true'
```
You should be aware that **ANY** field in the data module can be part of the search criteria.


### Environments

###### HEAD all environments
``` bash
# HEAD environments root
curl --head 'http://127.0.0.1:5150/v1/entities/Ent1/environments'
```

###### PUT an environment
``` bash
curl -H 'Content-Type: application/json' -D - -XPUT 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1' -d '{"name": "SoloEnvironmentOne"}'
```

###### HEAD an environment
``` bash
# HEAD environments root
curl --head 'http://127.0.0.1:5150/v1/entities/Ent1/environments/SoloEnv1'
```

###### POST one or many environments (bulk import)
``` bash
curl -H 'Content-Type: application/json' -D - -XPOST 'http://127.0.0.1:5150/v1/entities/Ent1/environments' -d '[{"env_id": "Env1", "tags": ["TestEnvironmentTagOne"], "contacts": {"person1": "4155551212", "person2": "email@person2.example.com"}, "name": "TestEnvironmentOne"}, {"env_id": "Env2", "tags": ["TestEnvironmentTagOne", "TestEnvironmentTagTwo"], "contacts": {"person1": "4155551212"}, "name": "TestEnvironmentTwo"}]'
```

###### GET environments
``` bash
curl -D - 'http://127.0.0.1:5150/v1/entities/x/environments/Env2'
```

###### GET environments and search
``` bash
curl -D - 'http://127.0.0.1:5150/v1/entities/x/environments?contact=person1'
```

###### GET environments and search doing a partial match using provided criteria
``` bash
curl -D - 'http://127.0.0.1:5150/v1/entities/x/environments?tag=EnvironmentTag&fuzzy=true'
```
You should be aware that **ANY** field in the data module can be part of the search criteria.


### Devices

###### HEAD all devices
``` bash
curl --head http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices
```

###### PUT a device
``` bash
curl -H 'Content-Type: application/json' -D - -XPUT 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices/SoloDev1' -d '{"name": "SoloDeviceOne"}'
```

###### HEAD a device
``` bash
curl --head http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices/SoloDev1
```

###### POST one or many devices (bulk import)
``` bash
curl -H 'Content-Type: application/json' -D - -XPOST 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices' -d '[{"dev_id": "Dev1", "tags": ["TestEnvironmentTagOne"], "access_ip": {"drac": "172.16.24.1", "mgmt": "fe80::6656:fc1d:cd1:ddba"}, "rack_id": "TestRack1", "row_id": "TestRow1", "name": "TestDeviceOne"}, {"dev_id": "Dev2", "tags": ["TestDeviceTagOne", "TestDeviceTagTwo"], "access_ip": {"drac": "172.16.24.2", "mgmt": "fe80::6656:fc1d:cd1:ddbb"}, "rack_id": "TestRack2", "row_id": "TestRow1", "name": "TestDeviceTwo"}]'
```

###### GET devices
``` bash
curl 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices'
```

###### GET devices and search
``` bash
curl 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices?row_id=TestRow1'
```

###### GET devices and search doing a partial matching using provided criteria
``` bash
curl 'http://127.0.0.1:5150/v1/entities/Solo1/environments/SoloEnv1/devices?name=Test&fuzzy=true'
```
You should be aware that **ANY** field in the data module can be part of the search criteria.

----

### Utilities

Automated data population can be simply done using an Ansible playbook. [More on helpful playbooks can be found here](playbooks/README.md)
