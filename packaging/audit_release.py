"""Fail safely when release contents look private or unexpectedly large."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_PARTS = {".git", ".venv", ".build-venv", "venv", "build", "dist", "__pycache__", ".pytest_cache", ".pyinstaller-cache"}
BLOCKED_NAMES = {".env", "config.yaml", "webui_settings.json", "rh_object_info.json"}
BLOCKED_SUFFIXES = {
    ".har", ".session", ".conf", ".lic", ".safetensors", ".ckpt", ".onnx",
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv",
}
CONTENT_RULES = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(rb"gh[pousr]_[A-Za-z0-9_]{30,}"),
    "AWS access key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "OpenAI-style secret": re.compile(rb"sk-[A-Za-z0-9_-]{24,}"),
    "macOS user path": re.compile(rb"/" + rb"Users/[^/\s]+/"),
    "Windows user path": re.compile(rb"[A-Za-z]:\\\\" + rb"Users\\\\[^\\\s]+\\\\"),
}
MAX_SOURCE_BYTES = 5 * 1024 * 1024


def files_to_check():
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def main() -> int:
    problems: list[tuple[str, str]] = []
    for path in files_to_check():
        relative = path.relative_to(ROOT)
        lowered = path.name.lower()
        if lowered in BLOCKED_NAMES or path.suffix.lower() in BLOCKED_SUFFIXES:
            problems.append((str(relative), "blocked filename/type"))
            continue
        if path.stat().st_size > MAX_SOURCE_BYTES:
            problems.append((str(relative), "unexpected file larger than 5 MiB"))
            continue
        data = path.read_bytes()
        for label, pattern in CONTENT_RULES.items():
            if pattern.search(data):
                problems.append((str(relative), label))
    if problems:
        print("Release audit failed. Potentially private items:", file=sys.stderr)
        for path, label in problems:
            print(f"- {path}: {label}", file=sys.stderr)
        return 1
    print("Release audit passed: no blocked files or recognized secret patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
