def databases_from_schema(schema):
    if not schema["fibery/types"]:
        return []

    fibery_types = schema["fibery/types"]
    databases = []
    for database in filter(lambda t: not t["fibery/name"].startswith("fibery/"), fibery_types):
        databases.append(database["fibery/name"])
    return databases
