from __future__ import annotations

import base64
import json
import mimetypes
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3.1-flash-image-preview"


def _post(model: str, payload: dict, api_key: str) -> dict:
    url = f"{API_BASE}/{model}:generateContent"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"gemini api {e.code}: {body}") from None


def _extract_images(resp: dict) -> list[bytes]:
    images: list[bytes] = []
    for cand in resp.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                images.append(base64.b64decode(inline["data"]))
    if not images:
        raise RuntimeError(f"gemini returned no image. response: {json.dumps(resp)[:500]}")
    return images


def _request(parts: list[dict], model: str, n: int, api_key: str) -> list[bytes]:
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["Image"]},
    }
    results: list[bytes] = []
    for _ in range(n):
        resp = _post(model, payload, api_key)
        results.extend(_extract_images(resp))
    return results


def generate(prompt: str, *, model: str, n: int, api_key: str) -> list[bytes]:
    return _request([{"text": prompt}], model, n, api_key)


def edit(
    image_path: Path,
    prompt: str,
    *,
    model: str,
    n: int,
    api_key: str,
) -> list[bytes]:
    mime = mimetypes.guess_type(str(image_path))[0] or "image/png"
    data = base64.b64encode(Path(image_path).read_bytes()).decode("ascii")
    parts = [
        {"inlineData": {"mimeType": mime, "data": data}},
        {"text": prompt},
    ]
    return _request(parts, model, n, api_key)
