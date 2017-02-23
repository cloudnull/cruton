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


