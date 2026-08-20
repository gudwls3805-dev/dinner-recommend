# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
import traceback


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        result = {"step": "start"}
        try:
            result["step"] = "read_key"
            api_key = os.environ.get("GEMINI_API_KEY")
            result["has_key"] = bool(api_key)
            result["key_len"] = len(api_key) if api_key else 0

            result["step"] = "read_body"
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")
            result["body"] = body

            result["step"] = "call_gemini"
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            payload = json.dumps({
                "contents": [{"parts": [{"text": "저녁 메뉴 하나만 추천해줘"}]}]
            }).encode("utf-8")
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key or ""},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=18) as resp:
                raw = json.loads(resp.read().decode("utf-8"))
            result["step"] = "success"
            result["gemini_text"] = raw["candidates"][0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as e:
            result["error_type"] = "HTTPError"
            result["http_code"] = e.code
            result["http_body"] = e.read().decode("utf-8", "ignore")[:500]
        except Exception as e:
            result["error_type"] = type(e).__name__
            result["error_msg"] = str(e)
            result["trace"] = traceback.format_exc()[:800]

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"ok"}')
