"""Static local import graph audit for the current Python and TypeScript sources."""

import argparse
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def acyclic(graph):
    done, active = set(), set()

    def visit(node):
        if node in active:
            raise AssertionError(f"Circular import at {node}")
        if node in done:
            return
        active.add(node)
        for dependency in graph[node]:
            visit(dependency)
        active.remove(node)
        done.add(node)

    for node in graph:
        visit(node)


def audit():
    source = ROOT / "backend/src"
    modules = {".".join(p.relative_to(source).with_suffix("").parts).removesuffix(".__init__"): p
               for p in (source / "smart_retail").rglob("*.py")}
    python_graph = {name: set() for name in modules}
    for name, path in modules.items():
        text = path.read_text(encoding="utf-8")
        assert "smart-retail-layout" not in text
        for node in ast.walk(ast.parse(text)):
            imports = []
            if isinstance(node, ast.ImportFrom):
                imports = [(node.module or "") + "." + a.name for a in node.names]
                imports.append(node.module or "")
            elif isinstance(node, ast.Import):
                imports = [a.name for a in node.names]
            for dependency in imports:
                if name.startswith("smart_retail.domain"):
                    assert not dependency.startswith(("fastapi", "sqlalchemy", "pymongo", "gridfs", "pydantic", "smart_retail.api", "smart_retail.application", "smart_retail.infrastructure"))
                if name.startswith("smart_retail.engines"):
                    assert not dependency.startswith(("fastapi", "sqlalchemy", "pymongo", "gridfs", "smart_retail.api", "smart_retail.application", "smart_retail.infrastructure"))
                if dependency in modules and dependency != name:
                    python_graph[name].add(dependency)
    frontend = ROOT / "frontend/src"
    ts_files = {p.resolve() for p in frontend.rglob("*") if p.suffix in (".ts", ".tsx")}
    ts_graph = {p: set() for p in ts_files}
    for path in ts_files:
        text = path.read_text(encoding="utf-8")
        assert "smart-retail-layout" not in text
        imports = re.findall(r'\bfrom\s+[\'"]([^\'"]+)[\'"]|\bimport\s*\(\s*[\'"]([^\'"]+)[\'"]', text)
        for pair in imports:
            relative = next(v for v in pair if v)
            if not relative.startswith("."):
                continue
            stem = path.parent / relative
            for candidate in (stem.with_suffix(".ts"), stem.with_suffix(".tsx"), stem / "index.ts", stem / "index.tsx"):
                if candidate.resolve() in ts_files:
                    ts_graph[path].add(candidate.resolve())
    acyclic(python_graph)
    acyclic(ts_graph)
    return {"python_modules": len(modules), "frontend_modules": len(ts_files), "cycles": [],
            "legacy_dependency_found": False, "forbidden_layer_imports": [],
            "scope": "Static application imports; excludes external dependency internals and runtime dynamic plugins",
            "python_edges": {k: sorted(v) for k, v in python_graph.items()},
            "frontend_edges": {str(k.relative_to(ROOT)): [str(p.relative_to(ROOT)) for p in sorted(v)] for k, v in ts_graph.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = audit()
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Architecture PASS:", result["python_modules"], "Python modules,", result["frontend_modules"], "frontend modules")
