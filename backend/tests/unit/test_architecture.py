import ast
from pathlib import Path


def test_dependency_direction():
    root = Path(__file__).resolve().parents[2] / "src/smart_retail"
    for folder, forbidden in [
        (
            "domain",
            (
                "fastapi",
                "sqlalchemy",
                "pydantic",
                "smart_retail.api",
                "smart_retail.infrastructure",
            ),
        ),
        ("engines", ("fastapi", "sqlalchemy", "smart_retail.api", "smart_retail.infrastructure")),
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
