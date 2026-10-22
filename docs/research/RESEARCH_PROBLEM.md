# Research problem

Support decisions across T1 shelf geometry, T2 category allocation, T3 physical SKU strip packing, and T4 customer/picker operations. All dimensions use m, mass kg and time s. The seven input groups are validated before execution.

Implemented scope: polygon/obstacles, rectangular shelves at 0/90 degrees, one shelf per category (several categories may share one shelf), one block per SKU with fixed facings. T4 uses grid shortest paths and single-server shelf queues. Integrated search compares finitely many complete T1-T4 candidates; it does not prove joint optimality.

The requested acceptance scope remains wider than this implementation. Status: RESEARCH_ACCEPTANCE_INCOMPLETE. See [acceptance matrix](ACCEPTANCE_MATRIX.md).
