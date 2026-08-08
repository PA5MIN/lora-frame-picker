"""Build desktop and WebUI binaries for the current operating system."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("PYINSTALLER_CONFIG_DIR", str(ROOT / ".pyinstaller-cache"))

import PyInstaller.__main__


def build() -> None:
    os.chdir(ROOT)
    for folder in (ROOT / "build", ROOT / "dist"):
        if folder.exists():
            shutil.rmtree(folder)
    bundle_mode = "--onedir" if sys.platform == "darwin" else "--onefile"
    common = ["--noconfirm", "--clean", bundle_mode]
    PyInstaller.__main__.run([
        *common,
        "--windowed",
        "--name", "LoRA-Frame-Picker",
        "lora_frame_picker.py",
    ])
    PyInstaller.__main__.run([
        *common,
        "--windowed",
        "--name", "LoRA-Phone-WebUI",
        "--add-data", f"webui_static{os.pathsep}webui_static",
        "lora_frame_picker_web.py",
    ])


if __name__ == "__main__":
    build()
