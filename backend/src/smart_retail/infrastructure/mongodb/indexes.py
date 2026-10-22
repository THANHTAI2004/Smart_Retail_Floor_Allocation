"""Idempotent non-TTL indexes; MongoDB's _id index supplies unique identities."""


def ensure_indexes(database):
    database.projects.create_index([("created_at", -1)], name="projects_created")
    database.optimization_runs.create_index(
        [("project_id", 1), ("created_at", -1)], name="runs_project_created"
    )
    database.optimization_runs.create_index(
        [("status", 1), ("created_at", 1)], name="queue_status_created"
    )
    database.optimization_runs.create_index(
        [("worker_id", 1), ("lease_until", 1)], name="worker_lease"
    )
    database.optimization_runs.create_index(
        [("status", 1), ("lease_until", 1)], name="recovery_status_lease"
    )
    database.worker_heartbeats.create_index([("epoch", -1)], name="worker_seen")
    return {
        n: list(database[n].list_indexes())
        for n in ["projects", "optimization_runs", "worker_heartbeats"]
    }
