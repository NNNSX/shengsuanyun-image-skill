#!/usr/bin/env python3
"""Generate images through Shengsuanyun Router task API.

Docs used:
- https://global.modelmesh.info/multiModel/314
- https://docs.router.shengsuanyun.com/353574241e0

The script intentionally does not store API keys. Set SHENGSUANYUN_API_KEY
or pass --api-key at runtime.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


CREATE_URL = "https://router.shengsuanyun.com/api/v1/tasks/generations"
POLL_URL = "https://router.shengsuanyun.com/api/v1/tasks/generations/{request_id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create and poll a gpt-image-2 generation task via Shengsuanyun Router."
    )
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Prompt text.")
    prompt_group.add_argument("--prompt-file", help="UTF-8 text file containing the prompt.")

    parser.add_argument("-r", "--reference-image", action="append", default=[],
                        help="Optional reference image. May be a local path or http(s) URL. Repeatable.")
    parser.add_argument("--api-key", default=None,
                        help="API key. Prefer SHENGSUANYUN_API_KEY env var. Do not commit keys.")
    parser.add_argument("--env-file", default=None,
                        help="Optional .env file containing SHENGSUANYUN_API_KEY=...")
    parser.add_argument("--base-url", default=CREATE_URL,
                        help=f"Task creation URL. Default: {CREATE_URL}")
    parser.add_argument("--model", default="openai/gpt-image-2")
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--size", default="auto",
                        help="auto, 1024x1024, 1536x1024, 1024x1536, etc.")
    parser.add_argument("--quality", default="auto",
                        help="auto, low, medium, high, etc. Depends on router/model support.")
    parser.add_argument("--background", default="auto")
    parser.add_argument("--moderation", default="auto")
    parser.add_argument("--output-format", default="png",
                        help="png, jpeg, webp, if supported by current router/model.")
    parser.add_argument("--output-compression", type=int, default=100)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--out-dir", default="outputs/shengsuanyun")
    parser.add_argument("--name", default="image",
                        help="Output filename prefix.")
    parser.add_argument("--save-response", action="store_true",
                        help="Save create/poll JSON responses in the output directory.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print payload without calling the API.")
    return parser.parse_args()


def load_env_file(path: str | None) -> None:
    if not path:
        return
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_api_key(args: argparse.Namespace) -> str | None:
    load_env_file(args.env_file)
    return args.api_key or os.getenv("SHENGSUANYUN_API_KEY") or os.getenv("API_KEY")


def load_prompt(args: argparse.Namespace) -> str:
    if args.prompt is not None:
        return args.prompt
    return Path(args.prompt_file).read_text(encoding="utf-8").strip()


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in {"http", "https"}


def local_image_to_data_url(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Reference image not found: {path}")
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def normalize_reference_images(paths_or_urls: list[str]) -> list[str]:
    refs: list[str] = []
    for item in paths_or_urls:
        refs.append(item if is_url(item) else local_image_to_data_url(item))
    return refs


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    prompt = load_prompt(args)
    refs = normalize_reference_images(args.reference_image)

    payload: dict[str, Any] = {
        "background": args.background,
        "model": args.model,
        "moderation": args.moderation,
        "n": args.n,
        "output_compression": args.output_compression,
        "output_format": args.output_format,
        "prompt": prompt,
        "quality": args.quality,
        "size": args.size,
    }

    # Router docs expose both `image` and `images` for OpenAI image tasks.
    # Use both for one reference to maximize compatibility; use `images` for many.
    if refs:
        payload["images"] = refs
        if len(refs) == 1:
            payload["image"] = refs[0]
    return payload


def request_json(method: str, url: str, api_key: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Authorization": f"Bearer {api_key}"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return json.loads(text)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"raw": body}
        raise RuntimeError(f"HTTP {exc.code} from {url}: {json.dumps(parsed, ensure_ascii=False)}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc


def find_request_id(create_response: dict[str, Any]) -> str:
    candidates = [
        create_response.get("request_id"),
        create_response.get("id"),
        create_response.get("data", {}).get("request_id") if isinstance(create_response.get("data"), dict) else None,
        create_response.get("data", {}).get("id") if isinstance(create_response.get("data"), dict) else None,
    ]
    for value in candidates:
        if isinstance(value, str) and value:
            return value
    raise RuntimeError(f"Could not find request_id in create response: {json.dumps(create_response, ensure_ascii=False)}")


def status_text(response: dict[str, Any]) -> str:
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("status", "state", "task_status"):
            value = data.get(key)
            if isinstance(value, str):
                return value.lower()
    for key in ("status", "state", "task_status"):
        value = response.get(key)
        if isinstance(value, str):
            return value.lower()
    return ""


def extract_image_urls(response: dict[str, Any]) -> list[str]:
    urls: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"url", "image_url"} and isinstance(item, str) and is_url(item):
                    urls.append(item)
                elif key in {"image_urls", "images", "urls"} and isinstance(item, list):
                    for entry in item:
                        if isinstance(entry, str) and is_url(entry):
                            urls.append(entry)
                        else:
                            walk(entry)
                else:
                    walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(response)
    # Preserve order while deduplicating.
    return list(dict.fromkeys(urls))


def is_terminal_status(status: str) -> bool:
    return status in {"completed", "complete", "succeeded", "success", "failed", "error", "cancelled", "canceled"}


def has_failed(status: str) -> bool:
    return status in {"failed", "error", "cancelled", "canceled"}


def poll_until_done(api_key: str, request_id: str, interval: float, timeout: float) -> dict[str, Any]:
    poll_url = POLL_URL.format(request_id=request_id)
    deadline = time.monotonic() + timeout
    last_response: dict[str, Any] | None = None

    while time.monotonic() < deadline:
        response = request_json("GET", poll_url, api_key)
        last_response = response
        status = status_text(response)
        urls = extract_image_urls(response)
        if urls:
            return response
        if status:
            print(f"status={status}", file=sys.stderr)
        if status and is_terminal_status(status):
            if has_failed(status):
                raise RuntimeError(f"Task failed: {json.dumps(response, ensure_ascii=False)}")
            return response
        time.sleep(interval)

    raise TimeoutError(f"Timed out waiting for task {request_id}. Last response: {json.dumps(last_response, ensure_ascii=False)}")


def download_file(url: str, out_path: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "shengsuanyun-image-script/1.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        out_path.write_bytes(resp.read())


def extension_from_url(url: str, fallback: str) -> str:
    path = urllib.parse.urlparse(url).path
    suffix = Path(path).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return suffix
    return "." + fallback.lstrip(".")


def main() -> int:
    args = parse_args()
    api_key = resolve_api_key(args)
    if not api_key and not args.dry_run:
        print("Missing API key. Set SHENGSUANYUN_API_KEY or pass --api-key.", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(args)
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    create_response = request_json("POST", args.base_url, api_key, payload)
    request_id = find_request_id(create_response)
    print(f"request_id={request_id}", file=sys.stderr)

    if args.save_response:
        (out_dir / f"{args.name}_create_response.json").write_text(
            json.dumps(create_response, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    final_response = poll_until_done(api_key, request_id, args.poll_interval, args.timeout)
    if args.save_response:
        (out_dir / f"{args.name}_final_response.json").write_text(
            json.dumps(final_response, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    urls = extract_image_urls(final_response)
    if not urls:
        print("Task completed but no image URL was found. Final response:", file=sys.stderr)
        print(json.dumps(final_response, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    saved: list[str] = []
    for idx, url in enumerate(urls, start=1):
        ext = extension_from_url(url, args.output_format or "png")
        out_path = out_dir / f"{args.name}_{idx:02d}{ext}"
        download_file(url, out_path)
        saved.append(str(out_path))

    print(json.dumps({"request_id": request_id, "images": saved}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
