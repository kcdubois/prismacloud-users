# Prisma Cloud User scripts

This repository is used for simplifying some operational aspects of managing Prisma Cloud users using its API, with multi-tenant support.

## To get started

This project is built using Pipenv as a Python package manager as well a managing virtual environments for 
simpler use. If you already have Python 3.10 installed, here's a simple way to use these scripts.

```bash
pip install pipenv
pipenv install 
pipenv run python bin/user_init.py

> Creating the asset directory
> Writing roles.yaml.
> Writing users.yaml.
> Writing tenants.yaml.
```

Once the asset directory is populated, you can use the sync to add users to all tenants:
* users.yaml: Contains all the basic user information to create an admin user with SSO login
* roles.yaml: Contains the mappings of users-to-roles
* tenants.yaml: Contains all the tenant API keys and URLs

Once populated, you can run the sync script by running it inside the virtual environment:
```bash
pipenv run python bin/user_sync.py
```
## Security notes
The current implementation of tenant credentials being simplistic for the sake of a simple proof of concept, a long term
solution would be to create an integration that leverages one of the secret stores available on the market like Hashicorp 
Vault or cloud-native secret stores like AWS Systems Manager Parameters Store. 