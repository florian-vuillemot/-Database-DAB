import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.mark.parametrize('svc', [
  'mongod'
])
def test_is_enabled(host, svc):
    service = host.service(svc)

    assert service.is_enabled


@pytest.mark.parametrize('svc', [
    'mongod'
])
def test_is_running(host, svc):
    service = host.service(svc)

    assert service.is_running


def test_mongdb_org_is_installed_with_good_version(host):
    mongodb = host.package('mongodb-org')

    assert mongodb.version.startswith('4.2')


def test_primary_and_secondary(host):
    from pymongo import MongoClient

    mongo_client = MongoClient(host.interface("eth0").addresses, 27017)

    r = []
    for ha_member in mongo_client.admin.command('replSetGetStatus')['members']:
        r.append(ha_member['stateStr'])

    assert 'PRIMARY' in r
    assert 'SECONDARY' in r
