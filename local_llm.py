import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def generate_local(
        prompt: str,
        model: str = "qwen3.5:4b-q4_K_M",
        json_mode: bool = False
) -> str:
    payload = {
        "model" : model,
        "prompt": prompt,
        "stream": False,
        "Think": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 8192
        }
    }

    if json_mode:
        payload["format"] = "json"

    request = Request(
        url="http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urlopen(request, timeout=300) as response:
            result = json.load(response)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(
            f"Cannot complete Ollama request: {exc}"
        ) from exc

    answer = (result.get("response") or "").strip()

    if not answer:
        raise RuntimeError(
            "Ollama returned an empty final answer. "
            f"Stop reason: {result.get('done_reason')}. "
            f"Thinking characters: "
            f"{len(result.get('thinking') or '')}. "
            f"Generated tokens: {result.get('eval_count')}."
        )

    return answer