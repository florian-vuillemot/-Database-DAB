import os
import pytest

from pymongo import MongoClient
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
    mongo_client = MongoClient(host.interface("eth0").addresses, 27017)

    r = []
    for ha_member in mongo_client.admin.command('replSetGetStatus')['members']:
        r.append(ha_member['stateStr'])

    assert 'PRIMARY' in r
    assert 'SECONDARY' in r


def test_ensure_priority(host):
    members = _get_config_members(host)

    priority = []
    votes = []
    nb_hosts = len(members)

    for ha_member in members:
        priority.append(ha_member['priority'])
        votes.append(ha_member['votes'])

    assert nb_hosts - 1 == int(sum(priority))
    assert nb_hosts == sum(votes)


def test_one_slave_delay(host):
    members = _get_config_members(host)

    nb_slave_delay = []
    slaves_delay = []

    for ha_member in members:
        _slave_delay = ha_member['slaveDelay']
        slaves_delay.append(_slave_delay)
        nb_slave_delay.append(_slave_delay != 0)

    assert 5 == sum(slaves_delay)
    assert 1 == sum(nb_slave_delay)


def _get_config_members(host):
    mongo_client = MongoClient(host.interface("eth0").addresses, 27017)
    return mongo_client.admin.command('replSetGetConfig')['config']['members']
