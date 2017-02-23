## Installation of Cruton.

Installing the base system requirements
``` bash
apt-get install -y python-dev build-essential libssl-dev
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

