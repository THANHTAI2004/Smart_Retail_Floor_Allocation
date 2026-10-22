import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from pymongo.uri_parser import parse_uri


@dataclass(frozen=True)
class Settings:
    uri: str
    database: str

    @classmethod
    def load(cls, uri=None, database=None):
        local = Path(os.getenv("SMART_RETAIL_HOME", str(Path.cwd()))) / "var/mongodb/private.json"
        uri = (
            uri
            or os.getenv("MONGODB_URI")
            or (
                json.loads(local.read_text(encoding="utf-8"))["uri"]
                if local.exists()
                else "mongodb://127.0.0.1:27017"
            )
        )
        if not uri.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError("MongoDB URI required; SQL connection strings are retired")
        name = (
            database
            or parse_uri(uri).get("database")
            or os.getenv("MONGODB_DATABASE", "smart_retail")
        )
        name = str(name)
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,63}", name):
            raise ValueError("Invalid MongoDB database name")
        return cls(uri, name)
