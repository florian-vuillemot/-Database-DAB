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

from ansible.module_utils.basic import AnsibleModule
from pymongo import MongoClient


def get_ha_members(mongo_client):
    try:
        members = mongo_client.admin.command('replSetGetConfig')['config']['members']
    except:
        members = []
    return set(m['host'] for m in members)


def not_in_ha(ha_members: set, hosts: list) -> set:
    _hosts = set(f'{h}:27017' for h in hosts)
    return ha_members ^ _hosts


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


def run_module():
    # define available arguments/parameters a user can pass to the module
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
    if ha_members and not not_in_ha(ha_members, hosts):
        module.exit_json(changed=False)

    config = new_ha_config(hosts, delayed_members)
    mongo_client.admin.command('replSetInitiate', config)

    module.exit_json(changed=True)


def main():
    run_module()

if __name__ == '__main__':
    main()
