# Useful Playbooks

This directory contains useful playbooks.

----

##### Data population playbook. This playbook is used to scan through an environment and populate the system with real system data.

Usage:
``` bash
ansible-playbook -i "${INVENTORY_FILE}" populate-data.yml -e "api_endpoint=http://172.99.106.30:5150" -e "api_entity=Ent1" -e "api_environment=Env1"
```


##### Exercise the API making all calls

Usage:
``` bash
ansible-playbook -i "${INVENTORY_FILE}" api-exercise.yml -e "api_endpoint=http://172.99.106.30:5150"
```
