from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from urllib import error, request

import sys

for candidate in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
    if (candidate / "env_utils.py").exists():
        BOOTSTRAP_ROOT = candidate
        break
else:
    BOOTSTRAP_ROOT = Path(__file__).resolve().parents[3]

PROJECT_ROOT = BOOTSTRAP_ROOT
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from env_utils import find_project_root, load_project_env
from env_utils import get_wenxuan_output_dir

PROJECT_ROOT = find_project_root(Path(__file__).resolve())

load_project_env(PROJECT_ROOT, [Path.cwd() / ".env"])


DEFAULT_BASE_URL = "http://107.172.148.170:8000/v1"
DEFAULT_MODEL = "gpt-image-2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an image through a local OpenAI-compatible image API.")
    parser.add_argument("--prompt", required=True, help="Image prompt text")
    parser.add_argument("--out", help="Output image path. Defaults to ./wenxuan-output/generated-image.png")
    parser.add_argument("--api-key", help="API key; defaults to OPENAI_API_KEY")
    parser.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL), help="OpenAI-compatible base URL")
    parser.add_argument("--model", default=os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL), help="Image model")
    parser.add_argument("--n", type=int, default=1, help="Number of images to request")
    parser.add_argument("--response-format", default="b64_json", choices=["b64_json"], help="Response format")
    parser.add_argument("--size", default=os.environ.get("OPENAI_IMAGE_SIZE", ""), help="Optional image size, if supported by the server")
    return parser.parse_args()


def load_api_key(value: str | None) -> str:
    api_key = (value or os.environ.get("OPENAI_API_KEY", "")).strip()
    if not api_key:
        raise SystemExit("Missing API key. Set OPENAI_API_KEY or pass --api-key.")
    return api_key


def call_image_api(*, base_url: str, api_key: str, model: str, prompt: str, n: int, response_format: str, size: str) -> dict:
    url = base_url.rstrip("/") + "/images/generations"
    payload: dict[str, object] = {
        "model": model,
        "prompt": prompt,
        "n": n,
        "response_format": response_format,
    }
    if size:
        payload["size"] = size

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    req = request.Request(url, data=body, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail[:1000]}") from exc


def main() -> int:
    args = parse_args()
    api_key = load_api_key(args.api_key)
    default_out = get_wenxuan_output_dir() / "generated-image.png"
    out_path = Path(args.out).expanduser().resolve() if args.out else default_out.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    result = call_image_api(
        base_url=args.base_url,
        api_key=api_key,
        model=args.model,
        prompt=args.prompt,
        n=args.n,
        response_format=args.response_format,
        size=args.size,
    )

    images = result.get("data") or []
    if not images:
        raise SystemExit(f"No image returned: {json.dumps(result, ensure_ascii=False)[:1000]}")

    first = images[0]
    b64 = first.get("b64_json") if isinstance(first, dict) else None
    if not isinstance(b64, str) or not b64:
        raise SystemExit(f"Unexpected response payload: {json.dumps(result, ensure_ascii=False)[:1000]}")

    out_path.write_bytes(base64.b64decode(b64))
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
