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


def get_members(mongo_client):
    return mongo_client.admin.command('replSetGetConfig')['config']['members']


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        hosts=dict(type='list', required=True)
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    mongo_client = MongoClient('localhost', 27017)

    hosts = module.params.get('hosts')

    if not any(member['host'] not in hosts for member in get_members(mongo_client)):
        module.exit_json(changed=False)

    members = [{'_id': idx, 'host': f'{host}:27017'} for idx, host in enumerate(hosts)]
    config = {'_id': 'rs0', 'members': members}
    mongo_client.admin.command("replSetInitiate", config)

    result['original_message'] = module.params['name']
    result['message'] = 'New hosts added'

    if module.params['new']:
        result['changed'] = True

    #if module.params['name'] == 'fail me':
    #    module.fail_json(msg='You requested this to fail', **result)

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
