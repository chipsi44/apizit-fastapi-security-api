import asyncio
import json
import logging
import os
import socket
import uuid
import zlib

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from app.limits import FixtureBudget

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(FixtureBudget)
INSTANCE = uuid.uuid4().hex
STATE = {"completed": 0}
MAX_BODY = 65536


async def body_bytes(request):
    data = bytearray()
    async with asyncio.timeout(1):
        async for chunk in request.stream():
            if len(data) + len(chunk) > MAX_BODY:
                raise HTTPException(413, "fixture body cap")
            data.extend(chunk)
    return bytes(data)


@app.exception_handler(TimeoutError)
async def timeout_response(_request, _error):
    return JSONResponse({"status": "fixture_timeout"}, status_code=408)


@app.get("/health")
async def health():
    # Simulated external dependency: no third-party destination is contacted.
    """Health dépendance simulée. Attente asynchrone de 50 ms ; aucune connexion."""
    await asyncio.sleep(0.05)
    return {"status": "ok", "dependency": "simulated", "max_delay_seconds": 0.05}


@app.post("/request")
async def request_probe(request: Request):
    """Entrées volumineuses. Body 64 KiB, 64 headers, 16 KiB headers, query 8 KiB ; lecture 1
    s.
    """
    data = await body_bytes(request)
    headers = request.scope.get("headers", [])
    return {
        "body_bytes": len(data),
        "header_count": len(headers),
        "header_bytes": sum(len(k) + len(v) for k, v in headers),
        "query_bytes": len(request.scope.get("query_string", b"")),
        "query_pairs": len(request.query_params.multi_items()),
    }


@app.post("/json-depth")
async def json_depth(request: Request):
    """JSON imbriqué. Profondeur 32, body 64 KiB ; contrôle avant json.loads."""
    data = await body_bytes(request)
    # Scan nesting before json.loads, accounting for brackets inside strings.
    depth = maximum = 0
    quoted = escaped = False
    for value in data:
        if quoted:
            if escaped:
                escaped = False
            elif value == 92:
                escaped = True
            elif value == 34:
                quoted = False
        elif value == 34:
            quoted = True
        elif value in (91, 123):
            depth += 1
            maximum = max(maximum, depth)
            if depth > 32:
                raise HTTPException(413, "fixture nesting cap")
        elif value in (93, 125):
            depth -= 1
    try:
        json.loads(data)
    except (ValueError, RecursionError):
        raise HTTPException(400, "invalid synthetic JSON") from None
    return {"maximum_depth": maximum, "body_bytes": len(data)}


@app.post("/compression")
async def compression(request: Request):
    """Expansion gzip. 64 KiB compressés et décompressés ; un seul membre gzip."""
    data = await body_bytes(request)
    try:
        decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
        expanded = decoder.decompress(data, MAX_BODY + 1)
        if len(expanded) > MAX_BODY or decoder.unconsumed_tail:
            raise HTTPException(413, "fixture expansion cap")
        if not decoder.eof or decoder.unused_data:
            raise HTTPException(400, "one complete gzip member required")
    except zlib.error:
        raise HTTPException(400, "invalid synthetic gzip") from None
    return {"compressed_bytes": len(data), "expanded_bytes": len(expanded)}


@app.get("/response")
async def large_response():
    """Réponse volumineuse. 1 MiB fixe de données synthétiques."""
    return Response(b"x" * (1024 * 1024), media_type="application/octet-stream")


@app.get("/health-error")
async def health_error():
    """Health erreur volumineuse. Erreur 500 avec exactement 1 MiB synthétique."""
    return Response(b"x" * (1024 * 1024), status_code=500, media_type="text/plain")


@app.get("/stream")
async def stream():
    """Streaming borné. 32 fragments de 4 KiB ; attente totale programmée 320 ms."""

    async def chunks():
        for _ in range(32):
            await asyncio.sleep(0.01)
            yield b"x" * 4096

    return StreamingResponse(chunks(), media_type="application/octet-stream")


@app.get("/headers")
async def headers():
    """Multiples headers. 32 headers synthétiques de 128 caractères."""
    return Response("synthetic", headers={f"X-Fixture-{i}": "x" * 128 for i in range(32)})


@app.get("/codes")
async def codes(code: int = 500):
    """Codes applicatifs ambigus. Liste fixe : 200,400,402,403,404,409,429,500,503."""
    if code not in {200, 400, 402, 403, 404, 409, 429, 500, 503}:
        raise HTTPException(400, "unsupported fixture code")
    return JSONResponse({"origin": "customer_fixture", "code": code}, status_code=code)


async def finish_background():
    await asyncio.sleep(0.2)
    STATE["completed"] += 1


@app.post("/background")
async def background(tasks: BackgroundTasks):
    """Tâche ASGI après body. 1 tâche de 200 ms par appel ; 2 requêtes actives maximum."""
    tasks.add_task(finish_background)
    return {"status": "scheduled", "instance": INSTANCE, "delay_seconds": 0.2}


@app.get("/state")
async def state():
    """État global ASGI. 1 compteur et 1 identifiant de processus."""
    return {"instance": INSTANCE, **STATE}


@app.get("/dns")
async def dns():
    # Fixed localhost resolution only; no requester-selected hosts or metadata.
    """DNS localhost. 1 résolution de localhost, attente 1 s ; aucun hostname fourni par le
    client.
    """
    try:
        async with asyncio.timeout(1):
            results = await asyncio.get_running_loop().getaddrinfo(
                "localhost", 8766, type=socket.SOCK_STREAM
            )
        return {"target": "localhost", "results": len(results)}
    except (OSError, TimeoutError):
        return {"status": "unavailable", "target": "localhost"}


@app.get("/connections")
async def connections():
    """Connexions locales. Désactivé par défaut ; 4 GET localhost:8766, timeout 300 ms,
    deadline 1 s.
    """
    if os.getenv("ADVERSARIAL_LOOPBACK_PEER") != "1":
        raise HTTPException(403, "local controlled peer disabled")
    async with httpx.AsyncClient(
        timeout=0.3,
        follow_redirects=False,
        trust_env=False,
        limits=httpx.Limits(max_connections=4, max_keepalive_connections=0),
    ) as client:

        async def one():
            try:
                async with client.stream("GET", "http://127.0.0.1:8766/probe") as response:
                    # Inspect only a fixed marker header; never download a peer body.
                    return response.headers.get("X-Synthetic-Peer") == "apizit-v1"
            except httpx.HTTPError:
                return False

        async with asyncio.timeout(1):
            results = await asyncio.gather(*(one() for _ in range(4)))
    return {"attempts": 4, "controlled_peer_responses": sum(results), "target": "loopback"}


@app.get("/recursion")
async def recursion():
    # In-process HTTP simulation; NOT evidence about gateway/IAM/network isolation.
    """Récursion HTTP simulée. 3 niveaux, 3 GET vers un peer ASGI en mémoire."""

    async def peer(scope, _receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"synthetic-peer"})

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=peer), base_url="http://synthetic.invalid"
    ) as client:

        async def visit(depth):
            if depth == 0:
                return 0
            await client.get("/probe")
            return 1 + await visit(depth - 1)

        calls = await visit(3)
    return {"calls": calls, "depth_cap": 3, "mode": "in_process_simulation"}


@app.post("/logs")
async def logs():
    """Logs synthétiques. 16 lignes fixes, aucun contenu de requête."""
    for index in range(16):
        logging.getLogger("synthetic.adversarial").warning(
            'SYNTHETIC untrusted telemetry {"fixture":true,"sequence":%d}', index
        )
    return {"lines": 16, "contains_user_data": False}
