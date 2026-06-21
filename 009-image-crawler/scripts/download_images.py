#!/usr/bin/env python3
"""Search and download images by type and count via Firecrawl image search."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path.home() / "Desktop" / "photo"
MIN_BYTES = 80_000
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s\u4e00-\u9fff-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:40] or "image"


def build_query(image_type: str) -> str:
    q = image_type.strip()
    lower = q.lower()

    cn_map = {
        "二次元": "anime",
        "动漫": "anime",
        "插画": "anime illustration",
        "风景": "landscape scenery",
        "赛博朋克": "cyberpunk",
        "猫": "cat cute",
        "少女": "anime girl",
        "豪车": "luxury car supercar",
        "跑车": "sports car supercar",
        "汽车": "car automotive",
    }
    for cn, en in cn_map.items():
        if cn in q:
            q = q.replace(cn, en)
            break

    if any(k in lower for k in ("4k", "3840", "2160", "超清", "高清壁纸")):
        base = q
    elif any(k in lower for k in ("anime", "wallpaper", "girl", "boy", "landscape", "cyberpunk")):
        base = f"{q} 4k wallpaper"
    else:
        base = f"{q} wallpaper 4k"
    return f"{base} site:alphacoders.com OR site:wallhaven.cc"


def load_firecrawl_api_key() -> str | None:
    key = os.environ.get("FIRECRAWL_API_KEY")
    if key:
        return key
    mcp_path = Path.home() / ".cursor" / "mcp.json"
    if not mcp_path.exists():
        return None
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
        env = data.get("mcpServers", {}).get("firecrawl-mcp", {}).get("env", {})
        return env.get("FIRECRAWL_API_KEY")
    except (json.JSONDecodeError, OSError):
        return None


def search_images(query: str, limit: int) -> tuple[list[dict], str | None]:
    search_limit = min(max(limit * 3, limit), 100)
    cmd = [
        "firecrawl",
        "search",
        query,
        "--sources",
        "images",
        "--limit",
        str(search_limit),
        "--json",
    ]
    api_key = load_firecrawl_api_key()
    if api_key:
        cmd.extend(["--api-key", api_key])

    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    stdout = proc.stdout.strip()
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or stdout or "firecrawl search failed")

    payload = None
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            payload = json.loads(line)
            break
    if payload is None:
        payload = json.loads(stdout)
    if not payload.get("success"):
        raise RuntimeError(json.dumps(payload, ensure_ascii=False))

    images = payload.get("data", {}).get("images") or []
    return images, payload.get("id")


def normalize_url(url: str) -> str:
    if "/thumb-" in url and "alphacoders.com" in url:
        return re.sub(r"/thumb-\d+-", "/", url)
    return url


def pick_candidates(images: list[dict], count: int, min_width: int) -> list[dict]:
    seen: set[str] = set()
    ranked: list[tuple[int, dict]] = []

    for item in images:
        url = item.get("imageUrl") or item.get("url")
        if not url or not url.startswith("http"):
            continue
        url = normalize_url(url)
        if url in seen:
            continue
        seen.add(url)

        width = int(item.get("imageWidth") or 0)
        height = int(item.get("imageHeight") or 0)
        if min_width and width and width < min_width:
            continue
        score = width * height
        ranked.append((score, {**item, "imageUrl": url, "imageWidth": width, "imageHeight": height}))

    ranked.sort(key=lambda x: x[0], reverse=True)
    picked = [item for _, item in ranked[:count]]

    if len(picked) < count:
        for item in images:
            url = normalize_url(item.get("imageUrl") or "")
            if not url or url in seen:
                continue
            seen.add(url)
            picked.append({**item, "imageUrl": url})
            if len(picked) >= count:
                break

    return picked[:count]


def download_file(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    if len(data) < MIN_BYTES:
        raise ValueError(f"file too small ({len(data)} bytes)")
    dest.write_bytes(data)
    return len(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download images by type and count")
    parser.add_argument("--type", "-t", required=True, help="Image type, e.g. 二次元 / anime / 风景")
    parser.add_argument("--count", "-n", type=int, default=10, help="Number of images to download")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument(
        "--min-width",
        type=int,
        default=1920,
        help="Minimum image width (3840 for strict 4K)",
    )
    args = parser.parse_args()

    if args.count < 1:
        print("count must be >= 1", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    query = build_query(args.type)
    print(f"Search query: {query}")

    try:
        images, search_id = search_images(query, args.count)
    except Exception as exc:
        print(f"Search failed: {exc}", file=sys.stderr)
        return 1

    if not images:
        print("No images found.", file=sys.stderr)
        return 1

    candidates = pick_candidates(images, args.count, args.min_width)
    if not candidates and args.min_width > 1920:
        print(f"No images >= {args.min_width}px, retrying with min-width 1920...")
        candidates = pick_candidates(images, args.count, 1920)
    if not candidates:
        candidates = pick_candidates(images, args.count, 0)

    slug = slugify(args.type)
    ok = 0
    for i, item in enumerate(candidates, 1):
        url = item["imageUrl"]
        ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            ext = ".jpg"
        dest = args.output / f"{slug}_{i:02d}{ext}"
        try:
            size = download_file(url, dest)
            w = item.get("imageWidth") or "?"
            h = item.get("imageHeight") or "?"
            print(f"OK {i}/{args.count}: {dest.name} ({size // 1024} KB, {w}x{h})")
            ok += 1
        except Exception as exc:
            print(f"FAIL {i}: {exc}", file=sys.stderr)

    print(f"\nDone: {ok}/{args.count} saved to {args.output}")
    if search_id:
        print(f"Search ID: {search_id}")

    return 0 if ok > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
