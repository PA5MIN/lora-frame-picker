#!/bin/zsh
set -u
cd "$(dirname "$0")" || exit 1

pause_on_error() {
  print ""
  print "启动失败：$1"
  print "如仍无法解决，请把上方完整错误信息复制到 GitHub Issues。"
  read "?按回车键关闭…"
  exit 1
}

if [[ ! -x ".venv/bin/python" ]]; then
  command -v python3 >/dev/null 2>&1 || pause_on_error "未找到 Python 3。请从 https://www.python.org/downloads/macos/ 安装 Python 3.9 或更高版本。"
  python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' || pause_on_error "需要 Python 3.9 或更高版本。"
  print "首次运行：正在创建独立运行环境…"
  python3 -m venv .venv || pause_on_error "无法创建 .venv。请确认 Python 安装完整且当前文件夹可写。"
fi

LORA_VENV_PYTHON=".venv/bin/python"
if ! "$LORA_VENV_PYTHON" -c 'import cv2; from PIL import Image; import flask' >/dev/null 2>&1; then
  print "正在安装所需组件（OpenCV、Pillow、Flask）…"
  "$LORA_VENV_PYTHON" -m pip install --upgrade pip || pause_on_error "pip 更新失败，请检查网络连接。"
  "$LORA_VENV_PYTHON" -m pip install -r requirements.txt || pause_on_error "依赖安装失败，请检查网络或代理设置。"
fi

"$LORA_VENV_PYTHON" -c 'import tkinter' >/dev/null 2>&1 || pause_on_error "当前 Python 缺少 Tkinter。建议安装 python.org 提供的官方 Python。"
"$LORA_VENV_PYTHON" lora_frame_picker.py
LORA_EXIT_CODE=$?
[[ $LORA_EXIT_CODE -eq 0 ]] || pause_on_error "程序异常退出，错误码 $LORA_EXIT_CODE。"
