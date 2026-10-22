# MongoDB as the only persistence backend — 2026-10-22

Supersedes the SQL persistence choice in decision 0001. The user explicitly
requested complete removal after the MongoDB cutover was verified.

Project aggregates, immutable runs and fenced worker leases use synchronous
PyMongo repositories. Scientific payload overflow uses checksummed GridFS JSON;
native BSON archives replace SQL recovery as the current backup/restore path.
No SQL ORM, migration runner, driver or importer is shipped. Python's standard
library is not modified; application code never imports its SQL modules.

Historical application/campaign rows from 34 SQL databases were decoded into
`smart_retail_history`, with source hashes and row readback validation. Original
SQL bytes and retired scripts were verified in an external backup before removal.
Scientific manifests/results remain unchanged; historical SQL counts and receipts
remain audit evidence. There is no runtime compatibility adapter for these archives.

The project venv and old experiment venv had SQLAlchemy/Alembic/SQL drivers removed.
Mypy uses filesystem caching rather than an SQL cache. Native backup assumes all
writers are stopped; it does not claim an online distributed snapshot. Compose,
Atlas and remote CI verification remain separate deployment work.
