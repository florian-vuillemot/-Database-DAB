import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.mark.parametrize('pkg', [
  'postgresql11-server'
])
def test_is_installed(host, pkg):
    package = host.package(pkg)

    assert package.is_installed


@pytest.mark.parametrize('svc', [
  'postgresql-11'
])
def test_is_enabled(host, svc):
    service = host.service(svc)

    assert service.is_enabled


@pytest.mark.parametrize('svc', [
    'postgresql-11'
])
def test_is_running(host, svc):
    service = host.service(svc)

    assert service.is_running


def test_client_connection(host):
    cmd = host.run("su - postgres -c /test_postgres_users")
    print(cmd.stdout)
    assert cmd.succeeded
