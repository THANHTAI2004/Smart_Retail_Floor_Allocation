import ast
import importlib.util
from pathlib import Path


def test_dependency_direction():
    root = Path(__file__).resolve().parents[2] / "src/smart_retail"
    for folder, forbidden in [
        (
            "domain",
            (
                "fastapi",
                "sqlalchemy",
                "pymongo",
                "gridfs",
                "pydantic",
                "smart_retail.api",
                "smart_retail.infrastructure",
            ),
        ),
        (
            "engines",
            (
                "fastapi",
                "sqlalchemy",
                "pymongo",
                "gridfs",
                "smart_retail.api",
                "smart_retail.infrastructure",
            ),
        ),
    ]:
        for path in (root / folder).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = (
                    [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else [alias.name for alias in node.names]
                    if isinstance(node, ast.Import)
                    else []
                )
                assert not any(name.startswith(forbidden) for name in names), path


def test_project_has_no_sql_persistence_imports_or_dependencies():
    root = Path(__file__).resolve().parents[2]
    forbidden = ("sqlite3", "sqlalchemy", "alembic", "psycopg", "psycopg2", "motor")
    for path in (root / "src").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = (
                [node.module or ""]
                if isinstance(node, ast.ImportFrom)
                else [a.name for a in node.names]
                if isinstance(node, ast.Import)
                else []
            )
            assert not any(n.split(".")[0] in forbidden for n in names), path
    for name in forbidden[1:]:
        assert importlib.util.find_spec(name) is None, name
