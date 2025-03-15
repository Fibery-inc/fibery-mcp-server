def databases_from_schema(schema):
    if not schema["fibery/types"]:
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
