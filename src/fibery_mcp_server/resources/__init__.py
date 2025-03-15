from pydantic import AnyUrl

from ..fibery_client import FiberyClient
from .schema import schema_uri, schema_resource, handle_schema


def list_all_resources():
    return [schema_resource]


async def handle_resource(fibery_client: FiberyClient, uri: AnyUrl):
    if str(uri) == schema_uri:
        return await handle_schema(fibery_client)
    else:
        raise ValueError(f"Resource '{uri}' is not defined.")


__all__ = [
    "list_all_resources",
    "handle_resource",
]