# Role Information

This roles allow to deploy a PostgreSQL database in Master-Slave replication. Another machines is plugs on the Slave, this allow cascading replication.

**Replication**
postgresql_master => postgresql_slave => postgresql_backup

# Requirements

Please, show the root `README.md`.

# Role Variables

Just filled the `vars/main.yml` file.

You have to provide the replication user and password
```
replication_username: replication
replication_username_password: Epitech42
```

And the users that will be allow to connect on the database:
```
users:
  - {db: 'test_db', name: 'foo', password: 'bar'}
  - {db: 'test_db2', name: 'foo2', password: 'bar2'}
```
