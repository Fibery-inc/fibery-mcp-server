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


def is_primitive(databases, field_type):
    return get_database_by_name(databases, field_type)["fibery/meta"].get("fibery/primitive?", False)


def is_enum(database):
    return database["fibery/meta"].get("fibery/enum?", False)


def is_collection(field):
    return field["fibery/meta"].get("fibery/collection?", False)


def is_title(field):
    return field["fibery/meta"].get("ui/title?", False)


def get_ref(databases, field):
    if is_primitive(databases, field["fibery/type"]):
        return None

    return get_database_by_name(databases, field["fibery/type"])


def process_fields(database, databases, collect_external_databases=False):
    fields = database["fibery/fields"]

    pretty_fields = []
    external_databases = []

    for field in fields:
        if field.get("fibery/meta").get("ui/hidden?"):
            continue
        title = field["fibery/name"].split('/')[-1].title()
        name = field["fibery/name"]
        field_type = field["fibery/type"]
        _is_primitive = is_primitive(databases, field_type)
        ref_database = get_ref(databases, field)
        _type = field["fibery/type"].split('/')[-1] if is_primitive else field_type
        if field_type == "fibery/rank":
            _type = "int"
        if is_enum(database) and is_title(field):
            _type += " ENUM"
        if ref_database:
            _type = field_type if not is_collection(field) else f"Collection({field_type})"
            if ref_database["fibery/name"] != database["fibery/name"] and ref_database["fibery/name"] not in map(lambda db: db["fibery/name"], external_databases):
                external_databases.append(ref_database)
        pretty_fields.append({"title": title, "name": name, "type": _type})
    return pretty_fields, external_databases
