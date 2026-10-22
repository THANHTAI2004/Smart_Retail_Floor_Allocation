"""Lossless JSON-backed overflow storage: no truncation or BSON integer coercion."""

import hashlib
import json
from dataclasses import asdict
from uuid import uuid4

from bson import BSON
from gridfs import GridFS


def canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class Payloads:
    def __init__(self, database):
        self.files = GridFS(database, collection="research_payloads")

    def pack(self, document, field, value):
        document[field] = value
        if value is None:
            return
        try:
            fits = len(BSON.encode({field: value})) < 4 * 1024**2
        except (OverflowError, ValueError, RecursionError):
            fits = False
        if fits:
            return
        raw = canonical(value)
        identifier = str(uuid4())
        # GridFS finishes publishing before a parent document references the blob.
        self.files.put(
            raw,
            _id=identifier,
            filename=field + ".json",
            metadata={"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)},
        )
        document[field] = None
        document[field + "_ref"] = {
            "id": identifier,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "encoding": "canonical-json-ascii-v1",
        }

    def unpack(self, document, field):
        reference = document.get(field + "_ref")
        if not reference:
            return document.get(field)
        raw = self.files.get(reference["id"]).read()
        if len(raw) != reference["bytes"] or hashlib.sha256(raw).hexdigest() != reference["sha256"]:
            raise ValueError("Stored research payload checksum mismatch")
        return json.loads(raw)


def record_document(record):
    document = asdict(record)
    document["_id"] = document.pop("id")
    return document


def record_value(cls, document):
    if document is None:
        return None
    names = cls.__dataclass_fields__
    return cls(
        **{
            k: document.get("_id") if k == "id" else document[k]
            for k in names
            if k == "id" or k in document
        }
    )
