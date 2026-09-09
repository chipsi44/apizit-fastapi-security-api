import asyncio
import gzip
from unittest.mock import AsyncMock

import httpx
import pytest

from app import app, routes
from app.limits import FixtureBudget


@pytest.fixture(autouse=True)
def isolate(monkeypatch):
    app.middleware_stack = None
    monkeypatch.delenv("ADVERSARIAL_LOOPBACK_PEER", raising=False)
    monkeypatch.setattr(routes, "STATE", {"completed": 0})

    async def deny_network(*_args, **_kwargs):
        raise AssertionError("Real HTTP network forbidden in tests")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", deny_network)


def call(method, path, **kwargs):
    async def invoke():
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://fixture.invalid"
        ) as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(invoke())


def test_health_and_request_shapes():
    assert call("GET", "/health").json()["dependency"] == "simulated"
    response = call(
        "POST",
        "/request?" + "&".join(f"p{i}=x" for i in range(128)),
        content=b"x" * 65536,
        headers={f"X-Synthetic-{i}": "x" * 128 for i in range(32)},
    )
    data = response.json()
    assert data["body_bytes"] == 65536
    assert data["query_pairs"] == 128
    assert data["header_count"] >= 32
    assert call("POST", "/request", content=b"x" * 65537).status_code == 413


def test_body_cap_without_content_length():
    async def chunks():
        yield b"x" * 40000
        yield b"x" * 40000

    assert call("POST", "/request", content=chunks()).status_code == 413


def test_request_metadata_caps():
    assert call("POST", "/request?x=" + "x" * 8192).status_code == 431
    assert call("POST", "/request", headers={"X-Fixture": "x" * 16384}).status_code == 431
    assert call("POST", "/request", headers={f"X-{i}": "x" for i in range(65)}).status_code == 431


def test_body_timeout(monkeypatch):
    async def slow_body(_request):
        raise TimeoutError

    monkeypatch.setattr(routes, "body_bytes", slow_body)
    assert call("POST", "/request").status_code == 408


def test_json_nesting_and_escaped_brackets():
    assert (
        call("POST", "/json-depth", content=b"[" * 32 + b"0" + b"]" * 32).json()["maximum_depth"]
        == 32
    )
    assert call("POST", "/json-depth", content=b"[" * 33 + b"0" + b"]" * 33).status_code == 413
    assert call("POST", "/json-depth", json={"value": '["' * 40}).json()["maximum_depth"] == 1
    assert call("POST", "/json-depth", content=b"{oops").status_code == 400


def test_compression_expansion_and_members():
    assert (
        call("POST", "/compression", content=gzip.compress(b"x" * 65536)).json()["expanded_bytes"]
        == 65536
    )
    assert call("POST", "/compression", content=gzip.compress(b"x" * 65537)).status_code == 413
    for data in (b"bad", gzip.compress(b"ok")[:-1], gzip.compress(b"a") + gzip.compress(b"b")):
        assert call("POST", "/compression", content=data).status_code == 400


def test_response_and_stream_bounds():
    assert len(call("GET", "/response").content) == 1024 * 1024
    error = call("GET", "/health-error")
    assert error.status_code == 500
    assert len(error.content) == 1024 * 1024
    assert len(call("GET", "/stream").content) == 32 * 4096
    response = call("GET", "/headers")
    fixture_headers = [
        value for key, value in response.headers.items() if key.startswith("x-fixture-")
    ]
    assert len(fixture_headers) == 32
    assert all(len(value) == 128 for value in fixture_headers)


@pytest.mark.parametrize("code", [200, 400, 402, 403, 404, 409, 429, 500, 503])
def test_customer_status_origin(code):
    response = call("GET", f"/codes?code={code}")
    assert response.status_code == code
    assert response.json()["origin"] == "customer_fixture"


def test_codes_invalid():
    assert call("GET", "/codes?code=302").status_code == 400
    assert call("GET", "/codes?code=invalid").status_code == 422


def test_background_and_state():
    assert call("POST", "/background").status_code == 200
    assert call("GET", "/state").json()["completed"] == 1


def test_network_disabled_and_simulated_recursion():
    assert call("GET", "/connections").status_code == 403
    assert call("GET", "/recursion").json() == {
        "calls": 3,
        "depth_cap": 3,
        "mode": "in_process_simulation",
    }


def test_dns_fixed_localhost(monkeypatch):
    async def run():
        resolver = AsyncMock(return_value=[("synthetic",)])
        monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", resolver)
        assert (await routes.dns())["results"] == 1
        assert resolver.call_args.args == ("localhost", 8766)

    asyncio.run(run())


def test_connections_fixed_target_no_redirects_or_body(monkeypatch):
    monkeypatch.setenv("ADVERSARIAL_LOOPBACK_PEER", "1")
    seen = []

    async def transport(_self, request):
        seen.append(str(request.url))
        return httpx.Response(200, headers={"X-Synthetic-Peer": "apizit-v1"})

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", transport)
    assert (
        call("GET", "/connections?target=http://169.254.169.254").json()[
            "controlled_peer_responses"
        ]
        == 4
    )
    assert seen == ["http://127.0.0.1:8766/probe"] * 4


def test_synthetic_logging(caplog):
    assert call("POST", "/logs").json()["lines"] == 16
    assert len(caplog.records) == 16
    assert all("SYNTHETIC" in record.message for record in caplog.records)


def test_budget_holds_until_whole_response_and_recovers_from_error():
    async def run():
        entered = asyncio.Event()
        finish = asyncio.Event()

        async def inner(_scope, _receive, _send):
            entered.set()
            await finish.wait()
            raise RuntimeError("synthetic")

        budget = FixtureBudget(inner)
        scope = {"type": "http"}
        send = AsyncMock()
        one = asyncio.create_task(budget(scope, None, send))
        await entered.wait()
        two = asyncio.create_task(budget(scope, None, send))
        await asyncio.sleep(0)
        await budget(scope, None, send)
        assert send.call_args_list[0].args[0]["status"] == 429
        finish.set()
        results = await asyncio.gather(one, two, return_exceptions=True)
        assert all(isinstance(result, RuntimeError) for result in results)
        assert budget.active == 0
        budget.used = 100
        send.reset_mock()
        await budget(scope, None, send)
        assert send.call_args_list[0].args[0]["status"] == 429

    asyncio.run(run())
