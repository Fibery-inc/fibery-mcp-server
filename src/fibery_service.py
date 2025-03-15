import os
import httpx
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()
__host = os.environ.get("FIBERY_HOST")
__token = os.environ.get("FIBERY_API_TOKEN")


async def fetch_from_fibery(
        url: str,
        method: str = "GET",
        json_data: Any = None,
        params: Dict[str, str] = None,
) -> Dict[str, Any]:
    """
    Generic function to fetch data from Fibery API

    Args:
        url: API endpoint path
        method: HTTP method
        params: Query parameters
        json_data: JSON body of the request

    Returns:
        Response data and metadata
    """

    if not __host:
        raise ValueError("Fibery host not provided. Set FIBERY_HOST environment variable.")

    if not __token:
        raise ValueError("Fibery API token not provided. Set FIBERY_API_TOKEN environment variable.")

    base_url = f"https://{__host}"
    headers = {
        "Authorization": f"Bearer {__token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30.0) as client:
        if method == "GET":
            response = await client.get(url, params=params)
        elif method == "POST":
            response = await client.post(url, json=json_data, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()

        return {
            "data": response.json() if response.content else None,
        }


async def get_schema() -> Dict[str, Any]:
    """
    Returns:
        Processed Fibery schema
    """
    result = await fetch_from_fibery(
        "/api/schema",
        method="GET",
        params={"with-description": "true", "with-soft-deleted": "false"},
    )

    schema_data = result["data"]

    return schema_data


if __name__ == '__main__':
    import asyncio

    async def test_fetch():
        res = await fetch_from_fibery('/api/schema', 'GET')
        print(res)

    asyncio.run(test_fetch())
