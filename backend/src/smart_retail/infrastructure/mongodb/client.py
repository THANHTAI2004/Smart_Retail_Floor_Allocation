"""Client ownership and narrow repository scope, no implicit unit-of-work mutation."""

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from smart_retail.infrastructure.mongodb.indexes import ensure_indexes
from smart_retail.infrastructure.mongodb.project_repository import Projects
from smart_retail.infrastructure.mongodb.serializers import Payloads
from smart_retail.infrastructure.mongodb.settings import Settings
from smart_retail.infrastructure.mongodb.worker_repository import Workers


class MongoStore(Projects, Workers):
    def __init__(self, settings):
        self.settings = settings
        self.client: MongoClient = MongoClient(
            settings.uri,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000,
            socketTimeoutMS=10000,
            appname="smart-retail",
            retryWrites=True,
            w="majority",
            journal=True,
        )
        self.database = self.client[settings.database]
        self.payloads = Payloads(self.database)

    def ready(self):
        try:
            self.database.command("ping")
            ensure_indexes(self.database)
        except PyMongoError:
            raise RuntimeError(
                "BLOCKED_MONGODB_RUNTIME: MongoDB is unavailable or not authorized; check environment privately"
            ) from None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def dispose(self):
        self.client.close()


def connect(uri=None, database=None):
    store = MongoStore(Settings.load(uri, database))
    return store, lambda: store
