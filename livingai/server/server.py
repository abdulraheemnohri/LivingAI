# LivingAI HTTP REST API Server
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
from .api import APIHandlers


class RequestHandler(BaseHTTPRequestHandler):
    handlers: APIHandlers = None

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self._set_headers(200)

    def do_GET(self) -> None:
        if not self.handlers:
            self._set_headers(500)
            self.wfile.write(b'{"error": "Handlers not initialized"}')
            return

        path = self.path.split("?")[0]
        if path == "/api/status":
            res = self.handlers.handle_status()
        elif path == "/api/memory":
            res = self.handlers.handle_memory_list()
        elif path == "/api/goals":
            res = self.handlers.handle_goals_list()
        elif path == "/api/skills":
            res = self.handlers.handle_skills_list()
        elif path == "/api/doctor":
            res = self.handlers.handle_doctor()
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Endpoint not found"}')
            return

        self._set_headers(200)
        self.wfile.write(json.dumps(res, default=str).encode("utf-8"))

    def do_POST(self) -> None:
        if not self.handlers:
            self._set_headers(500)
            self.wfile.write(b'{"error": "Handlers not initialized"}')
            return

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            payload = {}

        path = self.path.split("?")[0]
        if path == "/api/chat" or path == "/api/ask":
            res = self.handlers.handle_chat(payload)
            self._set_headers(200)
            self.wfile.write(json.dumps(res, default=str).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Endpoint not found"}')


class APIServer:
    """Embedded HTTP REST API Server for LivingAI."""

    def __init__(self, app: Any, host: str = "127.0.0.1", port: int = 8080):
        self.app = app
        self.host = host
        self.port = port
        self.handlers = APIHandlers(app)
        RequestHandler.handlers = self.handlers
        self.httpd = None

    def start(self) -> None:
        logging.info(f"Starting LivingAI API Server at http://{self.host}:{self.port}")
        print(f"🚀 LivingAI Local REST API Server running at http://{self.host}:{self.port}")
        self.httpd = HTTPServer((self.host, self.port), RequestHandler)
        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down API Server.")
            self.stop()

    def stop(self) -> None:
        if self.httpd:
            self.httpd.shutdown()
            logging.info("LivingAI API Server stopped")
