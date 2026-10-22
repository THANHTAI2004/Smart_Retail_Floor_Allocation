# Smart Retail engineering instructions

The 2026-10-21 user request explicitly replaces the previous architecture and
its Project-gated continuation workflow. The application lives directly in
`frontend/` and `backend/`. Do not restore `smart-retail-layout` as an application
dependency, create V2, or add compatibility layers to the retired implementation.

Read the current section at the top of HANDOFF.md, inspect Git status and the
relevant source before changes. Preserve unrelated dirty/untracked work, original
research documents and the Git index. Do not reset, clean, commit or push unless
the user explicitly authorizes that operation. Before replacing inherited data,
create and verify a recoverable external snapshot. The verified initial snapshot
and intact retired tree are recorded in docs/architecture/migration.md.

Use modular monolith boundaries: HTTP adapters -> application -> domain/engines;
infrastructure implements persistence. Engines cannot import API/ORM or choose
the end-to-end workflow. Use SI units (m, kg, s), immutable engine inputs, named
statuses, independent constraint replay, and explicit simulation assumptions.
Never label heuristic search failure as proven infeasibility.

Long numerical work runs in killable processes through the durable worker queue.
Each run owns an immutable input snapshot, source/dependency identity and checksums.
Do not reuse historical test counts as verification of new source. Record actual
commands, results, limitations and the next step in HANDOFF.md at each milestone.

Run the relevant checks from README. Keep schema fixtures, generated JSON schemas,
migrations and docs synchronized. Check Vietnamese text after scripted edits.
No sub-agent delegation is required for this repository.
