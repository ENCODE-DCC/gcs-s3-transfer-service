import json
from pathlib import Path
from typing import Any, Dict


def load_schema(schema_name: str) -> Dict[str, Any]:
    if not schema_name.endswith(".json"):
        schema_name = schema_name + ".json"
    current_dir = Path(__file__).resolve()
    schema_path = current_dir.parent / schema_name
    with open(schema_path) as f:
        return json.load(f)
