"""Primary MongoDB connection facade; historical SQL migrations are offline only."""

import os
from pathlib import Path

from smart_retail.infrastructure.mongodb.client import connect as connect
from smart_retail.infrastructure.repositories.contracts import ProjectRecord as ProjectRecord
from smart_retail.infrastructure.repositories.contracts import RunRecord as RunRecord

ROOT = Path(os.getenv("SMART_RETAIL_HOME", str(Path.cwd()))).resolve()
