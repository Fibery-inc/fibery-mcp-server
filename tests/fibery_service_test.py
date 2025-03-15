import os
import sys
import pytest
from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.fibery_service import fetch_from_fibery, get_schema

pytestmark = pytest.mark.skipif(
    not os.environ.get("FIBERY_HOST") or not os.environ.get("FIBERY_API_TOKEN"),
    reason="FIBERY_HOST or FIBERY_API_TOKEN environment variables not set"
)


async def test_fetch_from_fibery():
    """Test the basic fetch_from_fibery function with a simple request"""
    # Test a simple schema fetch
    result = await fetch_from_fibery(
        "/api/schema",
        method="GET",
        params={"with-description": "true", "with-soft-deleted": "false"},
    )

    # Verify we got some data back
    assert result["data"] is not None, "No data returned from fetch_from_fibery"
    assert "fibery/types" in result["data"], "Schema does not contain 'types' field"


async def test_get_schema():
    """Test the get_schema function"""
    schema = await get_schema()

    assert schema is not None, "No schema returned"
    assert "fibery/types" in schema, "Schema does not contain 'types' field"
    assert len(schema["fibery/types"]) > 0, "Schema contains no types"

    print(f"\nSchema contains {len(schema['fibery/types'])} types")
