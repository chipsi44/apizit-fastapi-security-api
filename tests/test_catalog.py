import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_matches_public_routes_and_readmes():
    scenarios = json.loads((ROOT / "scenarios.json").read_text(encoding="utf-8"))
    declared = {(item["method"], item["path"]) for item in scenarios}
    assert len(declared) == len(scenarios)
    for item in scenarios:
        readme = ROOT / "security-tests" / item["id"] / "README.md"
        text = readme.read_text(encoding="utf-8")
        assert f"{item['method']} {item['path']}" in text
        assert item["risk"] in text
        assert item["bounds"] in text
    if (ROOT / "apizit_linking.yaml").exists():
        from apizit_linking import compile_linking_file

        result = compile_linking_file(ROOT / "apizit_linking.yaml", ROOT)
        assert result.is_valid
        actual = {(route.definition.method, route.definition.path) for route in result.routes}
    else:
        source = ast.parse((ROOT / "app/routes.py").read_text(encoding="utf-8"))
        actual = set()
        for node in source.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and decorator.func.attr in {"get", "post"}
                ):
                    actual.add((decorator.func.attr.upper(), decorator.args[0].value))
    assert actual == declared
