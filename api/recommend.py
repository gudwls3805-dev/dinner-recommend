from http.server import BaseHTTPRequestHandler
import json
import os
import re
import requests

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)


def build_prompt(situation, mood, budget, exclude):
    exclude_line = f"- 제외할 재료/메뉴: {exclude}" if exclude else "- 제외할 재료/메뉴: 없음"
    return f"""너는 저녁 메뉴를 추천해주는 한국 음식 큐레이터야.
아래 사용자 조건에 맞춰 오늘 저녁 메뉴 3개를 추천해줘.

[조건]
- 상황: {situation}
- 기분: {mood}
- 예산(1인): {budget or '상관없음'}
{exclude_line}

[규칙]
- 한국에서 실제로 먹거나 배달 가능한 현실적인 메뉴로만.
- 제외 재료/메뉴는 절대 추천하지 마.
- 각 메뉴마다 왜 지금 상황·기분에 맞는지 한 문장으로 설명.
- 배달앱에 검색하면 바로 나올 검색어를 keyword에 넣어.
- emoji는 음식과 어울리는 이모지 1개.

반드시 아래 JSON 형식으로만, 다른 말 없이 응답해:
{{
  "comment": "오늘 같은 날엔 이거지! 같은 한 줄 코멘트",
  "menus": [
    {{"name": "메뉴명", "reason": "추천 이유 한 문장", "keyword": "배달앱 검색어", "emoji": "🍲"}},
    {{"name": "...", "reason": "...", "keyword": "...", "emoji": "..."}},
    {{"name": "...", "reason": "...", "keyword": "...", "emoji": "..."}}
  ]
}}"""


def parse_gemini_json(text):
    """모델 응답에서 JSON만 안전하게 추출."""
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_POST(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return self._send(500, {"error": "GEMINI_API_KEY가 설정되지 않았어요."})

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or "{}")
        except (ValueError, json.JSONDecodeError):
            return self._send(400, {"error": "잘못된 요청 형식이에요."})

        situation = (body.get("situation") or "").strip()
        mood = (body.get("mood") or "").strip()
        if not situation or not mood:
            return self._send(400, {"error": "상황과 기분은 필수예요."})

        prompt = build_prompt(situation, mood, body.get("budget", ""), body.get("exclude", ""))

        try:
            resp = requests.post(
                GEMINI_URL,
                headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.95, "maxOutputTokens": 900},
                },
                timeout=18,
            )
        except requests.exceptions.Timeout:
            return self._send(504, {"error": "AI 응답이 지연됐어요."})
        except requests.exceptions.RequestException:
            return self._send(502, {"error": "AI 서버에 연결하지 못했어요."})

        if resp.status_code != 200:
            return self._send(502, {"error": f"AI 오류 ({resp.status_code})"})

        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            data = parse_gemini_json(text)
            menus = data.get("menus", [])[:3]
            if not menus:
                raise ValueError("empty")
            return self._send(200, {"comment": data.get("comment", ""), "menus": menus})
        except (KeyError, IndexError, ValueError, json.JSONDecodeError):
            return self._send(502, {"error": "AI 응답을 이해하지 못했어요. 다시 시도해주세요."})

    def do_GET(self):
        self._send(200, {"status": "ok", "usage": "POST로 situation, mood, budget, exclude 전송"})
