from typing import Dict, Any, List

import httpx


class Field:
    def __init__(self, raw_field):
        self.__raw_field = raw_field
        self.__raw_meta = raw_field.get("fibery/meta", {})

    def is_primitive(self):
        return self.__raw_meta.get("fibery/primitive?", False)

    def is_collection(self):
        return self.__raw_meta.get("fibery/collection?", False)

    def is_title(self):
        return self.__raw_meta.get("ui/title?", False)

    def is_hidden(self):
        return self.__raw_meta.get("ui/hidden?", False)

    @property
    def type(self):
        return self.__raw_field["fibery/type"]

    @property
    def primitive_type(self):
        return self.__raw_field["fibery/type"].split('/')[-1]

    @property
    def name(self):
        return self.__raw_field["fibery/name"]

    @property
    def title(self):
        return self.__raw_field["fibery/name"].split('/')[-1].title()


class Database:
    def __init__(self, raw_database):
        self.__raw_database = raw_database
        self.__raw_meta = raw_database.get("fibery/meta", {})
        self.__fields: List[Field] = [Field(raw_field) for raw_field in raw_database["fibery/fields"]]

    def is_primitive(self):
        return self.__raw_meta.get("fibery/primitive?", False)

    def is_enum(self):
        return self.__raw_meta.get("fibery/enum?", False)

    def include_database(self) -> bool:
        return not (
                self.name.startswith("fibery/") or
                self.name.startswith('Collaboration~Documents') or
                self.name.endswith('-mixin') or
                self.name == "workflow/workflow"
        )

    @property
    def name(self):
        return self.__raw_database["fibery/name"]

    @property
    def fields(self):
        return self.__fields


class Schema:
    def __init__(self, raw_schema):
        self.__raw_schema = raw_schema
        self.__databases: List[Database] = [Database(raw_db) for raw_db in raw_schema["fibery/types"]]

    def databases_by_name(self) -> Dict[str, Database]:
        return {db.name: db for db in self.__databases}

    def include_databases_from_schema(self) -> List[Database]:
        if not self.__databases:
            return []

        databases = []

        for database in filter(lambda db: db.include_database(), self.__databases):
            databases.append(database)
        return databases


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


    async def get_schema(self) -> Schema:
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
        return Schema(schema_data)

    async def execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        result = await self.fetch_from_fibery(
            "/api/commands",
            method="POST",
            json_data=[
                {
                    "command": command,
                    "args": args,
                },
            ],
        )

        result = result["data"][0]
        return result

