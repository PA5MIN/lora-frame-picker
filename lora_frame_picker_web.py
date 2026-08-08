#!/usr/bin/env python3
"""Password-protected LAN WebUI for the LoRA Frame Picker."""

from __future__ import annotations

import argparse
import base64
import ipaddress
import json
import os
import re
import secrets
import socket
import sys
import threading
import unicodedata
import webbrowser
from pathlib import Path

from flask import Flask, abort, jsonify, request, send_from_directory
from werkzeug.serving import make_server


APP_FOLDER = "LoRA Frame Picker"
ALLOWED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff",
    ".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv",
}
MAX_UPLOAD_BYTES = 12 * 1024 * 1024 * 1024
ACCESS_KEY = os.environ.get("LORA_WEBUI_KEY", secrets.token_urlsafe(18))
SERVER_INSTANCE = None
SERVER_URLS: list[str] = []
LAN_NETWORKS = tuple(ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


def resource_root() -> Path:
    """Locate read-only bundled files in source and PyInstaller builds."""
    bundled = getattr(sys, "_MEIPASS", None)
    return Path(bundled) if bundled else Path(__file__).resolve().parent


def data_root() -> Path:
    """Return a user-writable settings directory on every supported OS."""
    override = os.environ.get("LORA_FRAME_PICKER_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_FOLDER


RESOURCE_ROOT = resource_root()
DATA_ROOT = data_root()
SETTINGS_FILE = DATA_ROOT / "webui_settings.json"


def default_media_root() -> Path:
    return Path.home() / "Pictures" / APP_FOLDER


def display_path(path: Path) -> str:
    """Hide the local account name in UI, browser responses, and screenshots."""
    expanded = path.expanduser().resolve()
    try:
        relative = expanded.relative_to(Path.home().resolve())
    except ValueError:
        return str(expanded)
    if relative == Path("."):
        return "~"
    # UI text is documentation-like rather than an OS path input. Always use
    # forward slashes so screenshots and API responses look identical on every OS.
    return f"~/{relative.as_posix()}"


def configured_directory(key: str, environment_name: str, fallback: str) -> Path:
    environment_value = os.environ.get(environment_name)
    if environment_value:
        return Path(environment_value).expanduser()
    try:
        settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        value = settings.get(key)
        if isinstance(value, str) and value.strip():
            return Path(value).expanduser()
    except (OSError, json.JSONDecodeError):
        pass
    return default_media_root() / fallback


UPLOAD_DIR = configured_directory("upload_dir", "LORA_WEBUI_UPLOAD_DIR", "Uploads")
EXPORT_DIR = configured_directory("export_dir", "LORA_WEBUI_EXPORT_DIR", "Exports")

app = Flask(
    __name__,
    static_folder=str(RESOURCE_ROOT / "webui_static"),
    static_url_path="/static",
)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


def allowed(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def safe_media_filename(original: str) -> str:
    """Keep useful Unicode names while removing path and OS-reserved characters."""
    basename = Path(original.replace("\\", "/")).name
    suffix = Path(basename).suffix.lower()
    stem = unicodedata.normalize("NFC", Path(basename).stem)
    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", stem).strip(" .")
    if not stem:
        stem = f"mobile-{secrets.token_hex(6)}"
    if stem.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
        stem = f"_{stem}"
    return f"{stem[:160]}{suffix}"


def require_key() -> None:
    query_key = request.args.get("key")
    header_key = request.headers.get("X-Lora-Key")
    if not secrets.compare_digest(query_key or header_key or "", ACCESS_KEY):
        abort(403)


@app.before_request
def protect_everything() -> None:
    if request.path == "/health" or request.path.startswith("/static/"):
        return
    require_key()


@app.after_request
def security_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; "
        "style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"
    )
    return response


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="文件过大：单个文件最大为 12 GiB"), 413


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/media")
def media_list():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(UPLOAD_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if path.is_file() and allowed(path.name):
            files.append({"name": path.name, "size": path.stat().st_size, "url": f"/media/{path.name}"})
    return jsonify(files=files)


@app.get("/api/paths")
def paths():
    return jsonify(upload_dir=display_path(UPLOAD_DIR), export_dir=display_path(EXPORT_DIR))


@app.get("/api/server-info")
def server_info():
    return jsonify(urls=SERVER_URLS)


@app.post("/api/shutdown")
def shutdown_server():
    if SERVER_INSTANCE is None:
        return jsonify(error="服务尚未就绪"), 409
    threading.Timer(0.2, SERVER_INSTANCE.shutdown).start()
    return jsonify(ok=True)


@app.post("/api/upload")
def upload():
    uploads = request.files.getlist("files")
    if not uploads:
        return jsonify(error="没有收到文件"), 400
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved = []
    for item in uploads:
        original = item.filename or ""
        if not original or not allowed(original):
            return jsonify(error=f"不支持的文件类型：{original or '未命名文件'}"), 400
        clean_name = safe_media_filename(original)
        target = UPLOAD_DIR / clean_name
        stem, suffix, number = target.stem, target.suffix, 2
        while target.exists():
            target = UPLOAD_DIR / f"{stem}-{number}{suffix}"
            number += 1
        item.save(target)
        saved.append(target.name)
    return jsonify(saved=saved)


@app.get("/media/<path:filename>")
def get_media(filename: str):
    if not allowed(filename):
        abort(404)
    return send_from_directory(UPLOAD_DIR, filename, conditional=True)


@app.post("/api/export")
def export_frame():
    payload = request.get_json(silent=True) or {}
    image = payload.get("image")
    source_name = safe_media_filename(str(payload.get("sourceName", "frame.jpg")))
    if not isinstance(image, str) or not image.startswith("data:image/jpeg;base64,"):
        return jsonify(error="导出数据无效"), 400
    try:
        raw = base64.b64decode(image.split(",", 1)[1], validate=True)
    except (ValueError, IndexError):
        return jsonify(error="无法读取 JPEG 数据"), 400
    if len(raw) > 40 * 1024 * 1024:
        return jsonify(error="导出的图片超过 40 MiB，已拒绝保存"), 400
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = Path(source_name).stem or "frame"
    target = EXPORT_DIR / f"{base}-{secrets.token_hex(5)}.jpg"
    target.write_bytes(raw)
    return jsonify(name=target.name, folder=display_path(EXPORT_DIR))


def lan_addresses() -> list[str]:
    """Discover private IPv4 addresses without platform-specific commands."""
    addresses: set[str] = set()
    try:
        for entry in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            addresses.add(entry[4][0])
    except OSError:
        pass
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # UDP connect selects a local interface but sends no packet.
        probe.connect(("192.0.2.1", 80))
        addresses.add(probe.getsockname()[0])
    except OSError:
        pass
    finally:
        probe.close()
    return sorted(address for address in addresses if is_lan_address(address))


def is_lan_address(address: str) -> bool:
    parsed = ipaddress.ip_address(address)
    return any(parsed in network for network in LAN_NETWORKS)


def choose_port(requested: int, host: str) -> int:
    for port in range(requested, requested + 20):
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind((host, port))
            return port
        except OSError:
            continue
        finally:
            probe.close()
    raise RuntimeError(f"端口 {requested} 到 {requested + 19} 均不可用")


def configure_paths() -> int:
    """Open native folder pickers and save only local paths."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print("无法打开目录选择器：当前 Python 缺少 Tkinter。", file=sys.stderr)
        return 1
    root = tk.Tk()
    root.withdraw()
    upload_dir = filedialog.askdirectory(title="选择手机上传素材的保存文件夹")
    if not upload_dir:
        root.destroy()
        return 0
    export_dir = filedialog.askdirectory(title="选择筛帧 JPEG 的导出文件夹")
    if not export_dir:
        root.destroy()
        return 0
    if Path(upload_dir).resolve() == Path(export_dir).resolve():
        messagebox.showerror("目录不可用", "上传目录与导出目录不能相同。")
        root.destroy()
        return 1
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(
        json.dumps({"upload_dir": upload_dir, "export_dir": export_dir}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    messagebox.showinfo("设置完成", "保存位置已更新，请重新启动 WebUI。")
    root.destroy()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LoRA Frame Picker LAN WebUI")
    parser.add_argument("--configure", action="store_true", help="choose upload and export folders")
    parser.add_argument("--host", default=os.environ.get("LORA_WEBUI_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("LORA_WEBUI_PORT", "8765")))
    parser.add_argument("--no-browser", action="store_true", help="do not open the local browser")
    return parser.parse_args()


def main() -> int:
    global SERVER_INSTANCE, SERVER_URLS
    args = parse_args()
    if args.configure:
        return configure_paths()
    if UPLOAD_DIR.resolve() == EXPORT_DIR.resolve():
        print("启动失败：上传目录与导出目录不能相同。请运行 --configure 重新设置。", file=sys.stderr)
        return 2
    port = choose_port(args.port, args.host)
    local_url = f"http://127.0.0.1:{port}/?key={ACCESS_KEY}"
    lan_urls = []
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        lan_urls = [f"http://{address}:{port}/?key={ACCESS_KEY}" for address in lan_addresses()]
    SERVER_URLS = lan_urls
    print("\nLoRA 数据集筛帧器 WebUI 已启动")
    print(f"电脑打开：{local_url}")
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        print("手机和电脑需连接同一个可信 Wi-Fi。请在手机打开：")
        for url in lan_urls:
            print(f"  {url}")
    print(f"\n手机上传目录：{display_path(UPLOAD_DIR)}")
    print(f"导出图片目录：{display_path(EXPORT_DIR)}")
    print("访问口令每次启动都会变化；不要把完整链接发给不信任的人。")
    print("按 Ctrl+C 停止服务。\n")
    server = make_server(args.host, port, app)
    SERVER_INSTANCE = server
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(local_url)).start()
    print(f"WebUI 正在监听 {args.host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWebUI 已停止。")
    finally:
        SERVER_INSTANCE = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
