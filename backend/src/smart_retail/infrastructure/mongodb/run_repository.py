import time

from pymongo import ReturnDocument
from pymongo.database import Database

from smart_retail.infrastructure.mongodb.serializers import (
    Payloads,
    record_document,
    record_value,
    sha,
)
from smart_retail.infrastructure.repositories.contracts import RunRecord


class Runs:
    database: Database
    payloads: Payloads

    def decode_run(self, document):
        if document is None:
            return None
        document = dict(document)
        for field in ("snapshot", "result"):
            document[field] = self.payloads.unpack(document, field)
        return record_value(RunRecord, document)

    def get_run(self, identifier):
        return self.decode_run(self.database.optimization_runs.find_one({"_id": identifier}))

    def insert_run(self, record):
        if sha(record.snapshot) != record.input_sha256:
            raise ValueError("Snapshot checksum mismatch before enqueue")
        if record.result is not None and sha(record.result) != record.result_sha256:
            raise ValueError("Result checksum mismatch")
        document = record_document(record)
        for field in ("snapshot", "result"):
            self.payloads.pack(document, field, getattr(record, field))
        self.database.optimization_runs.insert_one(document)

    def list_runs(self, project_id):
        return [
            self.decode_run(d)
            for d in self.database.optimization_runs.find({"project_id": project_id})
            .sort("created_at", -1)
            .limit(100)
        ]

    def cancel_run(self, identifier):
        # Single atomic pipeline: QUEUED -> CANCELLED, RUNNING -> CANCEL_REQUESTED.
        self.database.optimization_runs.find_one_and_update(
            {"_id": identifier, "status": {"$in": ["QUEUED", "RUNNING"]}},
            [
                {
                    "$set": {
                        "status": {
                            "$cond": [
                                {"$eq": ["$status", "QUEUED"]},
                                "CANCELLED",
                                "CANCEL_REQUESTED",
                            ]
                        }
                    }
                }
            ],
        )
        return self.get_run(identifier)

    def owned_filter(self, record, now=None):
        return {
            "_id": record.id,
            "worker_id": record.worker_id,
            "lease_token": record.lease_token,
            "lease_until": {"$gt": time.time() if now is None else now},
            "status": {"$in": ["RUNNING", "CANCEL_REQUESTED"]},
        }

    def publish(self, record, owner=None):
        if record.result is not None and sha(record.result) != record.result_sha256:
            raise ValueError("Result checksum mismatch before publication")
        values = {
            "status": record.status,
            "stage": record.stage,
            "error": record.error,
            "result_sha256": record.result_sha256,
        }
        self.payloads.pack(values, "result", record.result)
        query = self.owned_filter(owner or record)
        # A cancel arriving after the supervisor's final read wins atomically.
        final_status = {
            "$cond": [{"$eq": ["$status", "CANCEL_REQUESTED"]}, "CANCELLED", record.status]
        }
        pipeline = [
            {"$set": {**{k: {"$literal": v} for k, v in values.items()}, "status": final_status}}
        ]
        saved = self.database.optimization_runs.find_one_and_update(
            query, pipeline, return_document=ReturnDocument.AFTER
        )
        return self.decode_run(saved)

    def mark_worker_lost(self, record):
        self.database.optimization_runs.update_one(
            {
                "_id": record.id,
                "status": {"$in": ["RUNNING", "CANCEL_REQUESTED"]},
                "lease_until": {"$lte": time.time()},
            },
            {
                "$set": {
                    "status": "FAILED",
                    "error": {
                        "code": "WORKER_LOST",
                        "message": "Expired worker lease; previous artifacts retained",
                    },
                }
            },
        )
