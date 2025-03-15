import httpx
from typing import Dict, Any


class FiberyClient:
    def __init__(self, fibery_host, fibery_api_token):
        if not fibery_host:
            raise ValueError("Fibery host not provided. Set FIBERY_HOST environment variable.")

        if not fibery_api_token:
            raise ValueError("Fibery API token not provided. Set FIBERY_API_TOKEN environment variable.")

        self.__fibery_host = fibery_host
        self.__fibery_api_token = fibery_api_token

    async def fetch_from_fibery(
            self,
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

        base_url = f"https://{self.__fibery_host}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__fibery_api_token}",
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


    async def get_schema(self) -> Dict[str, Any]:
        """
        Returns:
            Processed Fibery schema
        """
        result = await self.fetch_from_fibery(
            "/api/schema",
            method="GET",
            params={"with-description": "true", "with-soft-deleted": "false"},
        )

        schema_data = result["data"]
        return schema_data

