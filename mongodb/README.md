# Role Information

This roles allow to deploy a MongoDB database in Master-Slave replication. We have 3 machines configures in clusters and one machine that can't become a Master.

**Replication**
mongodb0 => mongodb1 => 5s => mongodb2

MongoDB0 and mongodb1 are replicat in async and after 5 second the replication is done on mongodb2.

# Requirements

Please, show the root `README.md`.
