from typing import List

from .fibery_client import Schema, Database, Field


def get_ref(schema: Schema, field: Field) -> Database | None:
    if field.is_primitive():
        return None

    ref_database = schema.databases_by_name().get(field.type, None)
    if not ref_database or ref_database.is_primitive():
        return None

    return ref_database


def process_fields(schema: Schema, database: Database, collect_external_databases=False):
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
            _type = "int"
        if database.is_enum() and field.is_title():
            type_str += " ENUM"
        if ref_database:
            type_str = field_type if not field.is_collection() else f"Collection({field_type})"
            if (
                    collect_external_databases and
                    ref_database.name != database.name and
                    ref_database.name not in map(lambda db: db.name, external_databases)
            ):
                external_databases.append(ref_database)
        pretty_fields.append({"title": title, "name": name, "type": type_str})
    return pretty_fields, external_databases
