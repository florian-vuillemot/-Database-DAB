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
