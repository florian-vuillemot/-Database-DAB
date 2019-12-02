# Database in container

## How to run 

docker-compose up --build

Database are expose on 27017,27018,27019.

## Architecture

Create 3 MongoDB databases and configure there with another container.

This is not obtimal because we need to configure the cluster on the fly.
