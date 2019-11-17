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


def test_nginx_is_installed(host):
    mongodb = host.package('mongodb-org')

    assert mongodb.version.startswith('4.2')
