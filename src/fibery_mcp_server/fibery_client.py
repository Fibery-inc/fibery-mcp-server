from typing import Dict, Any, List
from dataclasses import dataclass

import httpx


class Field:
    def __init__(self, raw_field: Dict[str, Any]):
        self.__raw_field = raw_field
        self.__raw_meta = raw_field.get("fibery/meta", {})

    def is_primitive(self) -> bool:
        return self.__raw_meta.get("fibery/primitive?", False)

    def is_collection(self) -> bool:
        return self.__raw_meta.get("fibery/collection?", False)

    def is_title(self) -> bool:
        return self.__raw_meta.get("ui/title?", False)

    def is_hidden(self) -> bool:
        return self.__raw_meta.get("ui/hidden?", False)

    def is_rich_text(self) -> bool:
        return self.__raw_field.get("fibery/type", None) == "Collaboration~Documents/Document"

    def is_workflow(self) -> bool:
        return self.__raw_field.get("fibery/name", None) == "workflow/state"

    @property
    def type(self) -> str:
        return self.__raw_field["fibery/type"]

    @property
    def primitive_type(self) -> str:
        return self.__raw_field["fibery/type"].split("/")[-1]

    @property
    def name(self) -> str:
        return self.__raw_field["fibery/name"]

    @property
    def title(self) -> str:
        return self.__raw_field["fibery/name"].split("/")[-1].title()


class Database:
    def __init__(self, raw_database: Dict[str, Any]):
        self.__raw_database = raw_database
        self.__raw_meta = raw_database.get("fibery/meta", {})
        self.__fields: List[Field] = [Field(raw_field) for raw_field in raw_database["fibery/fields"]]

    def is_primitive(self) -> bool:
        return self.__raw_meta.get("fibery/primitive?", False)

    def is_enum(self) -> bool:
        return self.__raw_meta.get("fibery/enum?", False)

    def include_database(self) -> bool:
        return not (
            self.name.startswith("fibery/")
            or self.name.startswith("Collaboration~Documents")
            or self.name.endswith("-mixin")
            or self.name == "workflow/workflow"
        )

    def fields_by_name(self) -> Dict[str, Field]:
        return {field.name: field for field in self.__fields}

    @property
    def name(self) -> str:
        return self.__raw_database["fibery/name"]

    @property
    def fields(self) -> List[Field]:
        return self.__fields


class Schema:
    def __init__(self, raw_schema: Dict[str, Any]):
        self.__raw_schema: Dict[str, Any] = raw_schema
        self.__databases: List[Database] = [Database(raw_db) for raw_db in raw_schema["fibery/types"]]

    def databases_by_name(self) -> Dict[str, Database]:
        return {db.name: db for db in self.__databases}

    def include_databases_from_schema(self) -> List[Database]:
        if not self.__databases:
            return []

        databases: List[Database] = []

        for database in filter(lambda db: db.include_database(), self.__databases):
            databases.append(database)
        return databases

    @property
    def databases(self) -> List[Database]:
        return self.__databases


@dataclass
class CommandResponse:
    success: bool
    result: List[Dict[str, Any]] | Dict[str, Any]


@dataclass
class GetDocumentResponse:
    secret: str
    content: str


@dataclass
class CreateDocumentResponse:
    success: bool
    message: str


def normalize_str(s: str) -> str:
    return s.replace(" ", "_").replace("-", "_")


class FiberyClient:
    def __init__(self, fibery_host: str, fibery_api_token: str, fibery_https: bool = True):
        if not fibery_host:
            raise ValueError("Fibery host not provided. Set FIBERY_HOST environment variable.")

        if not fibery_api_token:
            raise ValueError("Fibery API token not provided. Set FIBERY_API_TOKEN environment variable.")

        self.__fibery_host: str = fibery_host
        self.__fibery_api_token: str = fibery_api_token
        self.__fibery_https: bool = fibery_https

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

    async def execute_command(self, command: str, args: Dict[str, Any]) -> CommandResponse:
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
        return CommandResponse(result["success"], result["result"])

    async def query(self, query: Dict[str, Any], params: Dict[str, Any] | None) -> CommandResponse:
        return await self.execute_command("fibery.entity/query", {"query": query, "params": params})

    async def get_enum_values(self, database_name: str) -> CommandResponse:
        result = await self.fetch_from_fibery(
            "/api/commands",
            method="POST",
            json_data=[
                {
                    "command": "fibery.entity/query",
                    "args": {
                        "query": {
                            "q/from": database_name,
                            "q/select": {"Id": ["fibery/id"], "Name": ["enum/name"]},
                            "q/limit": 100,
                        },
                        "params": {},
                    },
                },
            ],
        )

        result = result["data"][0]
        return CommandResponse(result["success"], result["result"])

    async def get_document_content(self, secret: str) -> str:
        result = await self.fetch_from_fibery(
            f"api/documents/{secret}?format=md",
            method="GET",
        )
        result = result["data"]
        return GetDocumentResponse(result["secret"], result["content"]).content

    async def create_or_update_document(
        self, secret: str, content: str, append: bool = False
    ) -> CreateDocumentResponse:
        result = await self.fetch_from_fibery(
            "/api/documents/commands",
            "POST",
            {
                "command": "create-or-update-documents" if not append else "create-or-append-documents",
                "args": [{"secret": secret, "content": content}],
            },
        )
        result_parsed: bool | Dict[str, Any] = result["data"]
        if result_parsed is True:
            return CreateDocumentResponse(True, "Document created/updated successfully")
        return CreateDocumentResponse(False, result_parsed.get("message", "Failed to create/update document."))

    async def create_entity(self, database: str, entity: Dict[str, Any]) -> CommandResponse:
        return await self.execute_command(
            "fibery.entity/create",
            {
                "type": database,
                "entity": entity,
            },
        )

    async def create_entities_batch(self, database: str, entities: List[Dict[str, Any]]) -> CommandResponse:
        return await self.execute_command(
            "fibery.command/batch",
            {
                "commands": list(map(lambda entity: {
                    "command": "fibery.entity/create",
                    "args": {
                        "type": database,
                        "entity": entity
                    }
                }, entities)),
            },
        )

    async def update_entity(self, database: str, entity: Dict[str, Any]) -> CommandResponse:
        return await self.execute_command(
            "fibery.entity/update",
            {
                "type": database,
                "entity": entity,
            },
        )

    async def delete_entity(self, database: str, fibery_id: str) -> CommandResponse:
        return await self.execute_command(
            "fibery.entity/delete",
            {
                "type": database,
                "entity": {
                    "fibery/id": fibery_id,
                },
            },
        )

    async def get_public_id_by_id(self, database: str, fibery_id: str) -> str | None:
        result = await self.query(
            {
                "q/from": database,
                "q/select": {"Public Id": "fibery/public-id"},
                "q/where": ["=", ["fibery/id"], "$id"],
                "q/limit": 1,
            },
            {"$id": fibery_id},
        )
        if not result.success:
            return None
        return str(result.result[0]["Public Id"])

    def compose_url(self, space: str, database: str, public_id: str) -> str:
        return f"{'https' if self.__fibery_https else 'http'}://{self.__fibery_host}/{normalize_str(space)}/{normalize_str(database)}/{public_id}"
