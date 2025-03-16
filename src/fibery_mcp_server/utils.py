from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

from .fibery_client import FiberyClient, Schema, Database, Field


@dataclass
class PrettyField:
    title: str
    name: str
    type: str


def get_ref(schema: Schema, field: Field) -> Database | None:
    if field.is_primitive():
        return None

    ref_database = schema.databases_by_name().get(field.type, None)
    if not ref_database or ref_database.is_primitive():
        return None

    return ref_database


def map_enum_values(enum_values: List[Dict[str, Any]]) -> str:
    return ", ".join([f'"{value["Name"]}"' for value in enum_values])


async def process_fields(
    fibery_client: FiberyClient, schema: Schema, database: Database, collect_external_databases: bool = False
) -> Tuple[List[PrettyField], List[Database]]:
    fields = database.fields

    pretty_fields = []
    external_databases: List[Database] = []

    for field in fields:
        if field.is_hidden():
            continue
        title = field.title
        name = field.name
        field_type = field.type

        ref_database = get_ref(schema, field)
        type_str = field.primitive_type if field.is_primitive() else field_type
        if field_type == "fibery/rank":
            type_str = "int"
        if field.is_rich_text():
            type_str = "fibery/document"
        if database.is_enum() and field.is_title():
            enum_values_response = await fibery_client.get_enum_values(database.name)
            type_str += f" # available values: {map_enum_values(enum_values_response.result)}"
        if database.name.split("/")[0] == "workflow" and field.title == "Type":
            type_str += ' # available values: "Not started", "Started", "Finished"'
        if ref_database and not field.is_rich_text():
            type_str = field_type if not field.is_collection() else f"Collection({field_type})"
            if (
                collect_external_databases
                and ref_database.name != database.name
                and ref_database.name not in map(lambda db: db.name, external_databases)
            ):
                external_databases.append(ref_database)
        pretty_fields.append(PrettyField(title, name, type_str))
    return pretty_fields, external_databases
