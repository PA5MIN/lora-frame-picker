#!/bin/zsh
set -u
cd "$(dirname "$0")" || exit 1

if [[ ! -x ".venv/bin/python" ]]; then
  print "请先双击 Start-LoRA-WebUI.command 完成首次安装。"
  read "?按回车键关闭…"
  exit 1
fi

".venv/bin/python" lora_frame_picker_web.py --configure
LORA_EXIT_CODE=$?
if [[ $LORA_EXIT_CODE -ne 0 ]]; then
  print "设置失败，错误码 $LORA_EXIT_CODE。"
  read "?按回车键关闭…"
fi
