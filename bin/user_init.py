""" 
Create the base files to be used by the user_sync.py script. 
"""
import os
from pathlib import Path
from typing import Any

import yaml


ASSETS_DIR = Path(os.getenv("ASSETS_DIR", "assets"))

DEFAULT_ROLES = [
    { "name": "System Admin", "users": [ "jdoe@example.com"] }
]

EMPTY_USERS = [
    {
        "firstName": "John",
        "lastName": "Doe",
        "email": "jdoe@example.com",
        "enabled": True
    }
]

EMPTY_TENANTS = [
    {
        "name": "",
        "access_key": "",
        "secret_key": "",
        "prisma_cloud_api": "https://api.ca.prismacloud.io"
    }
]

def main():
    if not ASSETS_DIR.exists():
        print("Creating the asset directory")
        ASSETS_DIR.mkdir()

    with open(ASSETS_DIR.joinpath("roles.yaml"), "w") as fp:
        print("Writing roles.yaml.")
        yaml.dump(DEFAULT_ROLES, fp)
    
    with open(ASSETS_DIR.joinpath("users.yaml"), "w") as fp:
        print("Writing users.yaml.")
        yaml.dump(EMPTY_USERS, fp)

    with open(ASSETS_DIR.joinpath("tenants.yaml"), "w") as fp:
        print("Writing tenants.yaml.")
        yaml.dump(EMPTY_TENANTS, fp)


if __name__ == "__main__":
    main()