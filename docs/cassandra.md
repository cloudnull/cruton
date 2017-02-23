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


