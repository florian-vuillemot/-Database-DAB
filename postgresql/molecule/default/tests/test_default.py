import os
import pytest

import testinfra.utils.ansible_runner
import psycopg2


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


@pytest.mark.parametrize('pkg', [
  'postgresql12-server'
])
def test_is_installed(host, pkg):
    package = host.package(pkg)

    assert package.is_installed


@pytest.mark.parametrize('svc', [
  'postgresql-12'
])
def test_is_enabled(host, svc):
    service = host.service(svc)

    assert service.is_enabled


@pytest.mark.parametrize('svc', [
    'postgresql-12'
])
def test_is_running(host, svc):
    service = host.service(svc)

    assert service.is_running


def test_then_databases_are_created(host):
    db_default = ['postgres', 'template0', 'template1']
    _host = host.interface("eth0").addresses[0]
    c_str = "dbname='test_db' user='foo' host='" + _host + "' password='bar'"
    conn = psycopg2.connect(c_str)
    cur = conn.cursor()
    cur.execute("""SELECT datname from pg_database""")
    rows = cur.fetchall()
    to_create = set(['test_db', 'test_db2', *db_default])
    created = set([r[0] for r in rows])
    assert not (to_create ^ created)
