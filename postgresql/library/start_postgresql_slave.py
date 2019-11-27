#!/usr/bin/python


ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: start_postgresql_slave

short_description: Configure a PostgreSQL instance in slave

version_added: "1.0"

description:
    - "Configure a PostgreSQL instance in slave of a master"

options:
    primary_hostname:
        description:
            - PostgreSQL master
        required: true
    replication_username:
        description:
            - Username use with REPLICATE access
        required: true
    password:
        description:
            - Username password's
        required: true

author:
    - Florian Vuillemot
'''

EXAMPLES = '''
- name: Add to postgresql_master machines from groups slave by using 'replication' user
  no_log: yes
  become: yes
  become_user: postgres
  start_postgresql_slave:
    primary_hostname: postgresql_master
    replication_username: replication
    password: {{ password }}
  notify:
    - "Start PostgreSQL"
    - "Enabled PostgreSQL"
  when: inventory_hostname in groups['slave']
'''

RETURN = ''''''


import os
from ansible.module_utils.basic import AnsibleModule


def run_module():
    module_args = dict(
        primary_hostname=dict(type='str', required=True),
        replication_username=dict(type='str', required=True),
        password=dict(type='str', required=True)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    pgdata = '/var/lib/pgsql/12/data'
    if os.listdir(pgdata):
        module.exit_json(changed=False)
    else:
        primary_hostname = module.params.get('primary_hostname')
        replication_username = module.params.get('replication_username')
        password = module.params.get('password')

        os.system('PGPASSWORD="%s" pg_basebackup -h %s -U %s -p 5432 -D %s -Fp -Xs -P -R' % (password, primary_hostname, replication_username, pgdata))
        module.exit_json(changed=True)


def main():
    run_module()


if __name__ == '__main__':
    main()
