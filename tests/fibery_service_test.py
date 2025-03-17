import os
import sys
import pytest
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.fibery_mcp_server.fibery_client import FiberyClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIBERY_HOST") or not os.environ.get("FIBERY_API_TOKEN"),
    reason="FIBERY_HOST or FIBERY_API_TOKEN environment variables not set",
)
__fibery_host, __fibery_api_token = (
    os.environ.get("FIBERY_HOST"),
    os.environ.get("FIBERY_API_TOKEN"),
)


async def test_get_schema() -> None:
    """Test the get_schema function"""
    fibery_client = FiberyClient(__fibery_host, __fibery_api_token)
    schema = await fibery_client.get_schema()

    assert schema is not None, "No schema returned"
    assert len(schema.databases) > 0, "Schema does not contain 'types' field"


async def test_create_entity() -> None:
    """Test the create_entity function"""
    fibery_client = FiberyClient(__fibery_host, __fibery_api_token)
    fibery_id = str(uuid4())
    creation_result = await fibery_client.create_entity(
        "Product Management/Item", {"fibery/id": fibery_id, "Product Management/Name": "Test"}
    )

    assert creation_result.success is True, "Entity creation failed"

    deletion_result = await fibery_client.delete_entity("Product Management/Item", fibery_id)
    assert deletion_result.success is True, "Entity deletion failed"
