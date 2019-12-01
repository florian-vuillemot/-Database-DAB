#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mongo_ha

short_description: Configure MongoDB in High Availability

version_added: "1.0"

description:
    - "Configure MongoDB in HA and allow to add a standby machine with a delay"

options:
    hosts:
        description:
            - List of host to add in HA
        required: true
    delayed_members:
        description:
            - Hash of hosts with the delay
        required: true

author:
    - Florian Vuillemot
'''

EXAMPLES = '''
- name: Configure mongodb0 and mongodb1 in HA
  mongo_ha:
    hosts:
      - mongodb0
      - mongodb1
  run_once: yes

- name: Configure mongodb0 and mongodb1 in HA and add mongodb2 in standy server with a delay of 5 seconds
  mongo_ha:
    hosts:
      - mongodb0
      - mongodb1
      - mongodb2
    delayed_members:
      mongodb2:
        delay: 5
  run_once: yes
'''

RETURN = ''''''


from time import sleep
from ansible.module_utils.basic import AnsibleModule
from pymongo import MongoClient


def get_ha_members(mongo_client):
    try:
        members = mongo_client.admin.command('replSetGetConfig')['config']['members']
    except:
        members = []
    return set(m['host'].replace(':27017', '') for m in members)


def not_in_ha(ha_hosts_members, hosts):
    _hosts = set(hosts)
    disjoint_hosts = ha_hosts_members ^ _hosts
    hosts_not_in_ha = disjoint_hosts & _hosts
    return hosts_not_in_ha


def new_ha_config(hosts, delayed_members):
    members = []

    for idx, host in enumerate(hosts):
        m = {'_id': idx, 'host': host + ':27017'}

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


def add_new_members(mongo_client, new_members):
    conf = mongo_client.admin.command({'replSetGetConfig': 1})
    for member in new_members:
        nb_member = len(conf['config']['members'])
        conf['config']['members'].append({
            '_id': nb_member,
            'host': member,
            'priority': 0,
            'votes': 0
        })
        conf['config']['version'] += 1

        mongo_client.admin.command('replSetReconfig', conf['config'])
        wait_status(mongo_client, 'SECONDARY', member)

        conf = mongo_client.admin.command({'replSetGetConfig': 1})
        _member = next(m for m in conf['config']['members'] if member in m['host'])
        _member['priority'] = 1
        _member['votes'] = 1
        conf['config']['version'] += 1
        mongo_client.admin.command('replSetReconfig', conf['config'])


def run_module():
    module_args = dict(
        hosts=dict(type='list', required=True),
        delayed_members=dict(type='dict', required=False, default={})
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
        add_new_members(mongo_client, new_members)
    else:
        config = new_ha_config(hosts, delayed_members)
        mongo_client.admin.command('replSetInitiate', config)
        wait_status(mongo_client, 'PRIMARY')

    module.exit_json(changed=True)


def main():
    run_module()

if __name__ == '__main__':
    main()
