# Introduction 
This school project it's about database replication. Beside theorical review we have to configure a database replication with MongoDB and PostgreSQL in Master-Slave and a third machine in backup.

There are **no** security consideration here.

This courses it's the following of the "Infinity-Storage" project.

# Getting Started
All this project can be deploy on Azure. If you want create this environment you can go in the directory Azure.

If you want to install a MongoDB or PostgreSQL database, go in the directory, filled the `inventory.cfg` and run `ansible-playbook -i inventory.cfg molecule/default/playbook.yml`. Don't forget to update you `~/.ansible.cfg` files by adding this directory in your roles.

# Build and Test
You need Python, Pipenv and docker to run this following part.

All the dependancies are in the Pipenv file.

Please, after installed Pipenv run `pipenv shell; pipenv install` to obtain a configuration up.

Go in the direcoties mongodb/postgresql and run `molecule test` to run tests.

You can also find the `azure-pipelines.yml` file that will allow you to run a test pipeline in Azure Devops.