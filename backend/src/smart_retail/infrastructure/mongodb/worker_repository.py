import time
from uuid import uuid4

from pymongo import ReturnDocument

from smart_retail.infrastructure.mongodb.run_repository import Runs


class Workers(Runs):
    def heartbeat(self, worker_id):
        self.database.worker_heartbeats.update_one(
            {"_id": worker_id}, {"$set": {"epoch": time.time(), "status": "ONLINE"}}, upsert=True
        )

    def worker_online(self):
        return (
            self.database.worker_heartbeats.find_one(
                {"epoch": {"$gt": time.time() - 10}, "status": "ONLINE"}
            )
            is not None
        )

    def claim(self, worker_id, now):
        document = self.database.optimization_runs.find_one_and_update(
            {"status": "QUEUED"},
            {
                "$set": {
                    "status": "RUNNING",
                    "worker_id": worker_id,
                    "lease_token": str(uuid4()),
                    "started_epoch": now,
                    "lease_until": now + 30,
                }
            },
            sort=[("created_at", 1)],
            return_document=ReturnDocument.AFTER,
        )
        return self.decode_run(document)

    def renew(self, record, stage=None):
        values = {"lease_until": time.time() + 30}
        if stage is not None:
            values["stage"] = stage
        updated = self.database.optimization_runs.update_one(
            self.owned_filter(record), {"$set": values}
        )
        return updated.modified_count == 1

    def recover_expired(self, now):
        count = 0
        for status, terminal in [("RUNNING", "TIMED_OUT"), ("CANCEL_REQUESTED", "CANCELLED")]:
            count += self.database.optimization_runs.update_many(
                {"status": status, "lease_until": {"$lte": now}},
                {
                    "$set": {
                        "status": terminal,
                        "error": {
                            "code": "WORKER_LOST",
                            "message": "Worker lease expired; old owner fenced out",
                        },
                    }
                },
            ).modified_count
        return count
