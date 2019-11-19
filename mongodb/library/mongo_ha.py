#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: my_test

short_description: This is my test module

version_added: "2.4"

description:
    - "This is my longer description explaining my test module"

options:
    name:
        description:
            - This is the message to send to the test module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_test:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the test module generates
    type: str
    returned: always
'''

from time import sleep
from ansible.module_utils.basic import AnsibleModule
from pymongo import MongoClient


def get_ha_members(mongo_client):
    try:
        members = mongo_client.admin.command('replSetGetConfig')['config']['members']
    except:
        members = []
    return set(m['host'].replace(':27017', '') for m in members)


def not_in_ha(ha_hosts_members: set, hosts: list) -> set:
    _hosts = set(hosts)
    disjoint_hosts = ha_hosts_members ^ _hosts
    hosts_not_in_ha = disjoint_hosts & _hosts
    return hosts_not_in_ha


def new_ha_config(hosts, delayed_members):
    members = []

    for idx, host in enumerate(hosts):
        m = {'_id': idx, 'host': f'{host}:27017'}

        if host in delayed_members:
            m.update({
                'priority': 0,
                'slaveDelay': delayed_members[host]['delay'],
                'hidden': True,
                'votes': 1
            })
        members.append(m)

    return {
        '_id': 'rs0',
        'members': members
    }


def wait_status(mongo_client, status, member_name=''):
    while True:
        for ha_member in mongo_client.admin.command('replSetGetStatus')['members']:
            if member_name in ha_member['name'] and ha_member['stateStr'] == status:
                return
        sleep(5)


def run_module():
    module_args = dict(
        hosts=dict(type='list', required=True),
        delayed_members=dict(type='list', required=False, default=[])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    mongo_client = MongoClient('localhost', 27017)

    hosts = module.params.get('hosts')
    delayed_members = module.params.get('delayed_members')

    ha_members = get_ha_members(mongo_client)
    if ha_members:
        new_members = not_in_ha(ha_members, hosts)
        if not new_members:
            module.exit_json(changed=False)
        conf = mongo_client.admin.command({'replSetGetConfig': 1})
        for member in new_members:
            nb_member = len(conf['config']['members'])
            conf['config']['members'].append({
                '_id': nb_member + 1,
                'host': member,
                'priority': 0,
                'votes': 0
            })
            conf['config']['version'] += 1
            mongo_client.admin.command('replSetReconfig', conf['config'])
            wait_status(mongo_client, 'SECONDARY', member)
            conf['config']['members'][-1]['priority'] = 1
            conf['config']['members'][-1]['votes'] = 1
            conf['config']['members'][-1]['hidden'] = False
            conf['config']['version'] += 1
            mongo_client.admin.command('replSetReconfig', conf['config'])
    else:
        config = new_ha_config(hosts, delayed_members)
        mongo_client.admin.command('replSetInitiate', config)
        wait_status(mongo_client, 'PRIMARY')

    module.exit_json(changed=True)


def main():
    run_module()

if __name__ == '__main__':
    main()
