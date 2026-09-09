"""Optional local-only peer: python tools/peer.py. Stop with Ctrl+C."""

from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    timeout = 1

    def do_GET(self):
        self.send_response(200 if self.path == "/probe" else 404)
        self.send_header("X-Synthetic-Peer", "apizit-v1")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, _format, *_args):
        pass


if __name__ == "__main__":
    with HTTPServer(("127.0.0.1", 8766), Handler) as server:
        server.timeout = 1
        for _ in range(100):
            server.handle_request()
