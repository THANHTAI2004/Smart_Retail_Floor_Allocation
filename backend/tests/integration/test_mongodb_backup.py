import json
import zipfile

import pytest

from smart_retail.infrastructure.mongodb.backup import backup, restore
from smart_retail.infrastructure.mongodb.client import connect


def test_native_backup_restores_documents_gridfs_and_indexes(database, saved_project, tmp_path):
    store = database[1]()
    raw = {"proof": [10**120 + 7, 10**100 + 3], "text": "x" * (5 * 1024**2)}
    document = {"_id": "large-proof"}
    store.payloads.pack(document, "result", raw)
    store.database.backup_proofs.insert_one(document)
    store.database.backup_proofs.create_index("label", unique=True, sparse=True)
    path = tmp_path / "native.zip"
    manifest = backup(store, path)
    target, _ = connect(database=database[0] + "_restored")
    try:
        restore(target, path)
        assert target.get_project(saved_project["id"]) == store.get_project(saved_project["id"])
        loaded = target.database.backup_proofs.find_one({"_id": "large-proof"})
        assert target.payloads.unpack(loaded, "result") == raw
        assert target.database.backup_proofs.index_information()["label_1"]["unique"]
        assert sum(c["documents"] for c in manifest["collections"]) > 1
    finally:
        target.dispose()


def test_restore_refuses_existing_target(database, saved_project, tmp_path):
    store = database[1]()
    path = tmp_path / "native.zip"
    backup(store, path)
    with pytest.raises(ValueError, match="empty target"):
        restore(store, path)
    assert store.get_project(saved_project["id"]) is not None


def test_restore_validates_all_checksums_before_writing(database, saved_project, tmp_path):
    store = database[1]()
    path = tmp_path / "native.zip"
    backup(store, path)
    corrupt = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(path) as original, zipfile.ZipFile(corrupt, "x") as changed:
        manifest = json.loads(original.read("manifest.json"))
        manifest["collections"][0]["sha256"] = "corrupt"
        for name in original.namelist():
            changed.writestr(
                name, json.dumps(manifest) if name == "manifest.json" else original.read(name)
            )
    target, _ = connect(database=database[0] + "_rejected")
    try:
        with pytest.raises(ValueError, match="checksum"):
            restore(target, corrupt)
        assert not target.database.list_collection_names()
    finally:
        target.dispose()
