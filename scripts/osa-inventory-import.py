#! /usr/bin/env python

import os
import sys
import json

import requests

DOCS = """
Parse an existing OpenStack-Ansible inventory and upload all of the known host data to the Cruton API.

USAGE:
python scripts/osa-inventory-import.py \
  ~/openstack_inventory-fcfs-iad3-3.json \
  http://172.99.106.30/v1/entities/TestEntity1/environments/TestEnvironment1/devices
"""


with open(os.path.expanduser(sys.argv[1])) as f:
    inventory = json.loads(f.read())

bulk_import = list()
for k, v in inventory['_meta']['hostvars'].items():
    dev = dict()
    dev['name'] = dev['dev_id'] = k
    dev['vars'] = v
    access_ip = dev['access_ip'] = dict()
    for _k, _v in v['container_networks'].items():
        address = _v.get('address')
        if address:
            access_ip[_k] = address

    tags = dev['tags'] = list()

    is_metal = v.pop('is_metal', False)
    if is_metal:
        tags.append('is_metal')

    component = v.pop('component', False)
    if component:
        tags.append(component)

    bulk_import.append(dev)

r = requests.post(
    url=sys.argv[2],
    data=json.dumps(bulk_import),
    headers={'Content-type': 'application/json', 'Accept': 'text/plain'}
)

# Return the API status code
print(r.status_code)
