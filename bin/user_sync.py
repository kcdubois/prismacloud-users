""" 
Sync local user role assignment across all the tenantns

"""
import os
from pathlib import Path
from typing import Any, TypeVar
from dataclasses import dataclass, asdict, field

import httpx
import yaml


ASSETS_DIR = Path(os.getenv("ASSETS_DIR", "assets"))
T = TypeVar("T")

# Dataclasses 

@dataclass
class Tenant:
    """ Tenant representation in local database. """
    name: str
    access_key: str
    secret_key: str
    prisma_cloud_api: str


@dataclass
class Role:
    """ Role representation in local database. """
    name: str
    users: list[str]
    id: str | None = None


@dataclass
class User:
    """ User representation in local database. """
    email: str
    firstName: str
    lastName: str
    enabled: bool
    roleIds: list[str] = field(default_factory=list)



class PrismaCloudApi:
    """ Prisma Cloud API Client. """
    def __init__(self, url: str, access_key: str, secret_key: str):
        self.url = url
        self.access_key = access_key
        self.secret_key = secret_key
        self.headers = { "Content-Type": "application/json" }

    @property
    def is_authenticated(self) -> bool:
        """ Checks if the access token is in the headers """
        return "x-redlock-auth" in self.headers

    def set_header(self, name: str, value: str) -> None:
        """ Sets a header to be added to upcoming requests. """
        self.headers[name] = value

    def login(self) -> None:
        """ Retrieve an access token from Prisma Cloud. """

        payload = { 
            "username": self.access_key,
            "password": self.secret_key
        }

        response = httpx.post(f"{self.url}/login", json=payload)

        response.raise_for_status()

        self.set_header("x-redlock-auth", response.json()['token'])

    def get_role_names(self) -> list[dict[str, Any]]:
        """ Requests list of default roles from Prisma Cloud. """

        response = httpx.get(f"{self.url}/user/role/name", headers=self.headers)
        response.raise_for_status()
        
        return response.json()

    def get_users_v3(self) -> list[dict[str, Any]]:
        """ Retrieves the list of users from Prisma Cloud. """

        response = httpx.get(f"{self.url}/v3/user", headers=self.headers)

        response.raise_for_status()

        return response.json()

    def create_user_v3(self, user: User) -> None:
        """ Creates a new user in Prisma Cloud and returns the user with an ID. """

        payload = asdict(user)
        default_role = user.roleIds[0]

        payload['defaultRoleId'] = default_role
        payload['timeZone'] = "America/Toronto"

        response = httpx.post(
            url=f"{self.url}/v3/user", 
            json=payload,
            headers=self.headers
        )

        response.raise_for_status()

    def update_user_v2(self, user: User) -> None:
        """ Updates an existing user in Prisma Cloud. """

        payload = asdict(user)

        response = httpx.put(
            url=f"{self.url}/v2/user/{user.email}",
            json=payload, headers=self.headers
        )
        
        response.raise_for_status()


def sync_users_with_tenant(api: PrismaCloudApi, tenant: Tenant, users: list[User]) -> None:
    """ Syncs users and roles to tenant """

    if not api.is_authenticated:
        api.login()
    prisma_cloud_users = api.get_users_v3()

    for user in users:
        if user.email not in [user['email'] for user in prisma_cloud_users ]:
            print(f"Tenant {tenant.name}: creating user {user.email}")
            api.create_user_v3(user)
            continue
    
        print(f"Tenant {tenant.name}: updating user {user.email}")
        api.update_user_v2(user)
    
    print(f"Sync for tenant {tenant.name} done, {len(users)} synced.")


def load_from_yaml(path: Path, dt: T) -> list[T]:
    """ Load data from YAML and convert to dataclass list. """
    with open(path) as fp:
        data = yaml.load(fp, Loader=yaml.CLoader)

    return [dt(**item) for item in data]


def map_role_ids_to_role(api: PrismaCloudApi, roles: list[Role]):
    """ Retrieves the tenant specific IDs of each built-in role. """

    if not api.is_authenticated:
        api.login()

    tenant_roles = api.get_role_names()

    for role in roles:
        tenant_role, = [item for item in tenant_roles if item['name'] == role.name]

        role.id = tenant_role['id']

    return roles


def map_roles_to_users(roles: list[Role], users: list[User]) -> list[User]:
    """ Add the role IDs to each user """
    for user in users:
        user.roleIds = [role.id for role in roles if user.email in role.users]

    return users


def main():
    if not ASSETS_DIR.exists():
        print("The asset directory can't be found, exiting...")
        exit(1)
    
    tenants = load_from_yaml(ASSETS_DIR.joinpath("tenants.yaml"), Tenant)
    roles = load_from_yaml(ASSETS_DIR.joinpath("roles.yaml"), Role)
    users = load_from_yaml(ASSETS_DIR.joinpath("users.yaml"), User)

    
    for tenant in tenants:
        api = PrismaCloudApi(
            url=tenant.prisma_cloud_api,
            access_key=tenant.access_key,
            secret_key=tenant.secret_key
        )

        api.login()

        roles_with_ids = map_role_ids_to_role(api, roles)
        users_with_roles = map_roles_to_users(roles_with_ids, users)

        print(f"=== Starting sync for tenant {tenant.name}")
        sync_users_with_tenant(api, tenant, users_with_roles)


if __name__ == "__main__":
    main()