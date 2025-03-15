import os
import sys
import pytest
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fibery_service import FiberyClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIBERY_HOST") or not os.environ.get("FIBERY_API_TOKEN"),
    reason="FIBERY_HOST or FIBERY_API_TOKEN environment variables not set"
)
__fibery_host, __fibery_api_token = os.environ.get("FIBERY_HOST"), os.environ.get("FIBERY_API_TOKEN")


async def test_get_schema():
    """Test the get_schema function"""
    fibery_client = FiberyClient(__fibery_host, __fibery_api_token)
    schema = await fibery_client.get_schema()

    assert schema is not None, "No schema returned"
    assert "fibery/types" in schema, "Schema does not contain 'types' field"
    assert len(schema["fibery/types"]) > 0, "Schema contains no types"

    print(f"\nSchema contains {len(schema['fibery/types'])} types")
