"""Native BSON backup/restore for a quiesced MongoDB database, including GridFS."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from bson import BSON, decode_file_iter, json_util

from smart_retail.infrastructure.mongodb.client import connect


def inspect(archive):
    manifest = json.loads(archive.read("manifest.json"))
    if manifest.get("format") != "smart-retail-bson-v1":
        raise ValueError("Unsupported backup format")
    for entry in manifest["collections"]:
        digest = hashlib.sha256()
        with archive.open(entry["file"]) as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError("Backup checksum mismatch")
        with archive.open(entry["file"]) as stream:
            if sum(1 for _ in decode_file_iter(stream)) != entry["documents"]:
                raise ValueError("Backup document count mismatch")
    return manifest


def backup(store, destination: Path):
    """Caller must stop all writers; no cross-collection snapshot is claimed."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": "smart-retail-bson-v1",
        "database": store.settings.database,
        "requires_quiesced_writers": True,
        "collections": [],
    }
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(store.database.list_collection_names()):
            if name.startswith("system."):
                continue
            filename = f"collections/{len(manifest['collections']):04d}.bson"
            digest, count = hashlib.sha256(), 0
            with archive.open(filename, "w") as stream:
                for document in store.database[name].find():
                    raw = BSON.encode(document)
                    stream.write(raw)
                    digest.update(raw)
                    count += 1
            indexes = json.loads(json_util.dumps(list(store.database[name].list_indexes())))
            manifest["collections"].append(
                {
                    "name": name,
                    "file": filename,
                    "sha256": digest.hexdigest(),
                    "documents": count,
                    "indexes": indexes,
                }
            )
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    with zipfile.ZipFile(destination) as archive:
        inspect(archive)
    return manifest


def restore(store, source: Path):
    """Refuse existing target and validate all bytes before the first insertion."""
    if store.database.list_collection_names():
        raise ValueError("Restore requires an empty target database; nothing overwritten")
    with zipfile.ZipFile(source) as archive:
        manifest = inspect(archive)
        for entry in manifest["collections"]:
            collection = store.database[entry["name"]]
            store.database.create_collection(entry["name"])
            with archive.open(entry["file"]) as stream:
                for document in decode_file_iter(stream):
                    collection.insert_one(document)
            for index in json_util.loads(json.dumps(entry["indexes"])):
                if index["name"] != "_id_":
                    options = {k: v for k, v in index.items() if k not in ("key", "v", "ns")}
                    collection.create_index(list(index["key"].items()), **options)
            if collection.count_documents({}) != entry["documents"]:
                raise ValueError("Restore readback count mismatch")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["backup", "restore"])
    parser.add_argument("path", type=Path)
    parser.add_argument("--database", required=True)
    parser.add_argument("--writers-stopped", action="store_true")
    args = parser.parse_args()
    if args.operation == "backup" and not args.writers_stopped:
        parser.error("Stop all writers and specify --writers-stopped")
    store, _ = connect(database=args.database)
    try:
        store.database.command("ping")
        result = (
            backup(store, args.path) if args.operation == "backup" else restore(store, args.path)
        )
        print(
            json.dumps(
                {
                    "status": "PASS",
                    "database": args.database,
                    "collections": len(result["collections"]),
                    "documents": sum(c["documents"] for c in result["collections"]),
                }
            )
        )
    finally:
        store.dispose()


if __name__ == "__main__":
    main()
