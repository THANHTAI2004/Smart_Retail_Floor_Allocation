from bson import BSON
from pymongo import ReturnDocument
from pymongo.database import Database

from smart_retail.infrastructure.mongodb.serializers import record_document, record_value
from smart_retail.infrastructure.repositories.contracts import ProjectRecord


class Projects:
    database: Database

    def get_project(self, identifier):
        return record_value(ProjectRecord, self.database.projects.find_one({"_id": identifier}))

    def create_project(self, record):
        document = record_document(record)
        if len(BSON.encode(document)) > 8 * 1024**2:
            raise ValueError("Project aggregate exceeds 8 MiB BSON budget")
        self.database.projects.insert_one(document)

    def list_projects(self):
        return [
            record_value(ProjectRecord, d)
            for d in self.database.projects.find().sort("created_at", -1)
        ]

    def save_project(self, identifier, revision, sections):
        if len(BSON.encode({"sections": sections})) > 8 * 1024**2:
            raise ValueError("Project aggregate exceeds 8 MiB BSON budget")
        document = self.database.projects.find_one_and_update(
            {"_id": identifier, "revision": revision},
            {"$set": {"sections": sections}, "$inc": {"revision": 1}},
            return_document=ReturnDocument.AFTER,
        )
        return record_value(ProjectRecord, document)
