from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from specter.model_provider import ModelRequest, OpenAICompatibleHttpProvider


def test_openai_compatible_provider_sends_completion_contract(monkeypatch) -> None:
    # Tests the OpenAI completion payload and authentication against a fake HTTP endpoint.
    captured: dict[str, object] = {}

    class CompletionHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            body_length = int(self.headers["Content-Length"])
            captured["path"] = self.path
            captured["authorization"] = self.headers.get("Authorization")
            captured["payload"] = json.loads(self.rfile.read(body_length))
            response = json.dumps(
                {
                    "choices": [{"text": "provider response"}],
                    "usage": {"completion_tokens": 2},
                }
            ).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), CompletionHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setenv("SPECTER_TEST_API_KEY", "secret-key")
    try:
        provider = OpenAICompatibleHttpProvider(
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="SPECTER_TEST_API_KEY",
            model_override="served-model",
        )
        result = provider.complete(
            ModelRequest(
                model="trace-model",
                prompt="Evaluate this response.",
                max_tokens=42,
                temperature=0.25,
            )
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    assert captured == {
        "path": "/v1/completions",
        "authorization": "Bearer secret-key",
        "payload": {
            "model": "served-model",
            "prompt": "Evaluate this response.",
            "max_tokens": 42,
            "temperature": 0.25,
        },
    }
    assert result.text == "provider response"
    assert result.token_count == 2
