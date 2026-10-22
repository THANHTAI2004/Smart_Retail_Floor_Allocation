"""Explicit, non-destructive migration of the current application's input bundle."""

import copy

from smart_retail.contracts.inputs import SECTIONS


def normalize(sections: dict) -> tuple[dict, list[dict]]:
    result = copy.deepcopy(sections)
    migrations = []
    for key, model in SECTIONS.items():
        if key not in sections:
            continue
        value = copy.deepcopy(sections[key])
        version = value.get("schema_version", "1.0")
        if version not in ("1.0", "1.1"):
            raise ValueError(f"Unsupported {key} schema version {version}")
        value["schema_version"] = "1.1"
        result[key] = model.model_validate(value).model_dump(mode="json")
        if version != "1.1":
            migrations.append({"section": key, "from": version, "to": "1.1"})
    return result, migrations
