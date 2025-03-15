def databases_from_schema(schema):
    if not schema.get("fibery/types"):
        return []

    fibery_types = schema["fibery/types"]
    databases = []

    def include_database(name: str) -> bool:
        return not (
                name.startswith("fibery/") or
                name.startswith('Collaboration~Documents') or
                name.endswith('-mixin') or
                name == "workflow/workflow"
        )

    for database in filter(lambda t: include_database(t["fibery/name"]), fibery_types):
        databases.append(database["fibery/name"])
    return databases


def get_database_by_name(databases, name):
    return next((db for db in databases if db["fibery/name"] == name), None)


def process_fields(databases, fields):
    pretty_fields = []
    for field in fields:
        if field.get("fibery/meta").get("ui/hidden?"):
            continue
        title = field["fibery/name"].split('/')[-1].title()
        name = field["fibery/name"]
        field_type = field["fibery/type"]
        is_primitive = get_database_by_name(databases, field_type)["fibery/meta"].get("fibery/primitive?", False)
        _type = field["fibery/type"].split('/')[-1] if is_primitive else field_type
        if field_type == "fibery/rank":
            _type = "int"
        pretty_fields.append({"title": title, "name": name, "type": _type})
    return pretty_fields
