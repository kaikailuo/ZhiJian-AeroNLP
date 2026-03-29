import re
import json
from typing import Any, Dict
import httpx


def parse_notam_text(raw_text: str, provider: str | None = None, api_key: str | None = None) -> Dict[str, Any]:
    if provider and api_key:
        parsed = _parse_with_llm(raw_text, provider, api_key)
        if parsed:
            return parsed
    return _parse_with_regex(raw_text)


def _parse_with_regex(raw_text: str) -> Dict[str, Any]:
    airport_match = re.search(r"A\)\s*([A-Z0-9]{4})", raw_text)
    runway_match = re.search(r"RWY\s*([0-9]{2}[A-Z]?/[0-9]{2}[A-Z]?|[0-9]{2}[A-Z]?)", raw_text)
    status = "unknown"
    if re.search(r"\b(CLOSED|CLSD)\b", raw_text, re.IGNORECASE):
        status = "closed"
    elif re.search(r"\b(OPEN|OPN)\b", raw_text, re.IGNORECASE):
        status = "open"

    return {
        "airport": airport_match.group(1) if airport_match else None,
        "runway": runway_match.group(1) if runway_match else None,
        "status": status,
        "summary": raw_text[:160].strip(),
    }


def _parse_with_llm(raw_text: str, provider: str, api_key: str) -> Dict[str, Any] | None:
    base_url, model = _provider_defaults(provider)
    if not base_url or not model:
        return None

    system_prompt = (
        "You are a NOTAM parser. Return strict JSON object with keys: "
        "airport (string|null), runway (string|null), status (closed|open|restricted|unknown), summary (string)."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    if provider == "qwen":
        payload["extra_body"] = {"enable_thinking": False}

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
    except Exception:
        return None

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content")
    )
    if not content:
        return None
    try:
        parsed = json.loads(content)
    except Exception:
        return None
    if not isinstance(parsed, dict):
        return None
    return {
        "airport": parsed.get("airport"),
        "runway": parsed.get("runway"),
        "status": parsed.get("status", "unknown"),
        "summary": str(parsed.get("summary") or raw_text[:160].strip()),
    }


def _provider_defaults(provider: str) -> tuple[str | None, str | None]:
    p = provider.lower().strip()
    if p == "qwen":
        return "https://dashscope.aliyuncs.com/compatible-mode/v1", "qwen3-8b"
    if p == "deepseek":
        return "https://api.deepseek.com/v1", "deepseek-chat"
    if p == "openai":
        return "https://api.openai.com/v1", "gpt-4o-mini"
    if p == "dmx":
        return "https://www.dmxapi.com/v1", "gpt-4.1-nano"
    return None, None
