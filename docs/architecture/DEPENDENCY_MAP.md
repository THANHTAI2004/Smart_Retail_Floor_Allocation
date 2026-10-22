# Dependency map - current research platform

Primary database: MongoDB/PyMongo. Project/run/worker structural contracts are in
`infrastructure/repositories/contracts.py`; concrete repositories, serializers,
GridFS, indexes and client ownership are in `infrastructure/mongodb/`. API and
campaign adapters share the same native durable queue. The offline SQLite importer
is an explicit migration CLI only. Domain and engines import no PyMongo/GridFS.
See [migration acceptance](../migration/MONGODB_MIGRATION_ACCEPTANCE.md).

## Joint extension

```mermaid
flowchart TD
  Worker[Killable worker child] --> Dispatch[Application workflow dispatch]
  Dispatch --> Joint[Feedback coordinator]
  Joint --> Stages[Shared official stage workflow]
  Stages --> Engines[T1 / T2 / T3 / T4 engines]
  Engines --> Validate[Independent geometry / assignment / physical / route replay]
  Validate --> State[Immutable content-sealed joint snapshot]
  State --> Diagnose[T4 operational diagnostics]
  Diagnose --> Actions[Bounded T1 / T2 / T3 edits]
  Actions --> Stages
  State --> Accept[Strict descent acceptance and trace]
  Joint --> Exact[Finite Cartesian enumeration engine]
  Exact --> Eval[Application evaluation callback]
  Eval --> Stages
  Exact --> Proof[Domain-bound certificate]
  Proof --> Verifier[Separate mixed-radix verifier]
  Verifier --> Fresh[Fresh cache / official model re-evaluation]
```

Numerical engines import no API, ORM, application or infrastructure. The exact
engine receives an application-owned evaluator callback rather than choosing the
end-to-end workflow. `application/stage_workflow.py` contains shared T1-T4 and
decision replay; `application/workflow.py` handles mode dispatch and the original
bounded multistart path. StageCache remains an infrastructure implementation passed
through the application. Every evaluated joint state and event is written through
the worker observer before proceeding. Runtime/cache-hit telemetry is retained in
stage artifacts outside scientific result identities.

See [joint model scope](../research/JOINT_OPTIMIZATION_FORMULATION.md) and
[JO acceptance](../research/JOINT_OPTIMIZATION_ACCEPTANCE.md).

## Platform dependencies

```mermaid
flowchart TD
  UI[React shell / inputs / research dashboard] --> HTTP[FastAPI adapters]
  CLI[Experiment CLI] --> CAM[Application campaign service]
  HTTP --> APP[Application project / workflow services]
  HTTP --> CAM
  CAM --> GEN[Deterministic dataset generators]
  CAM --> QUEUE[Durable MongoDB run queue with atomic leases]
  APP --> QUEUE
  QUEUE --> SUP[Worker supervisor: wall / RSS / cancellation]
  SUP --> CHILD[Killable numerical child]
  CHILD --> WORK[Application workflow / dependency cache keys]
  WORK --> T1[T1 grid / local search / topology]
  WORK --> T2[T2 greedy / affinity MILP]
  WORK --> T3[T3 first-fit / facing strip MILP]
  WORK --> T4[T4 routing / finite picker / shelf queues]
  T1 --> DOMAIN[Frozen SI domain inputs]
  T2 --> DOMAIN
  T3 --> DOMAIN
  T4 --> DOMAIN
  CHILD --> CACHE[Infrastructure immutable JSON stage cache]
  CAM --> AUDIT[Independent witness validation]
  AUDIT --> REPORT[Statistical analysis / tables / Matplotlib]
```

Contracts are Pydantic adapters; domain/engines do not import HTTP/ORM/application.
Shared navigation is an engine utility depending on geometry/domain only. Source
identity includes backend Python source, complete installed dependency versions,
HiGHS version and explicit model versions. Every queue job binds that identity.

Stage invalidation keys:

| Stage | Direct dependencies |
|---|---|
| T1 | Floorplan, shelf definitions/poses/mode, variant, layout algorithm/iteration budget |
| T2 | Placed shelves, categories including affinity, floor/entrance, T2 algorithm/weights |
| T3 | Placed shelves, products/facing ranges/compatibility, assignment, T3 algorithm |
| T4 | Placed shelves, planogram, assignment, floor/connectors, demand/picker/policy, orders/products, seed |

Every stage additionally binds source/dependency/model identity and job wall
budget. Time-limited MILP incumbents are not published as reusable cache entries.
Changing only product data reuses independent T1/T2, recomputes T3/T4. A queue
rerun with changed inputs is therefore a partial recomputation by dependency,
while each run still owns a complete immutable snapshot and stage evidence.

Execution order: contracts -> independently verified engines -> integrated/cache
workflow -> generator -> campaign runner -> analysis/report -> dashboard -> pilot
-> controlled main campaign -> replay/clean-environment verification -> readiness.

Run scripts/verify_architecture.py for the executable local import graph audit.
Static graph validation does not claim browser rendering or external-library
cycle analysis; those have separate test evidence.
