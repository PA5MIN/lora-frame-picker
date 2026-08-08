# LoRA 数据集筛帧器

从视频中挑选清晰画面，批量预览、裁剪和整理 LoRA 训练图片。软件在本地运行，支持 Windows 10/11、Apple Silicon Mac 和 Intel Mac。

[English](README_EN.md)

![LoRA 数据集筛帧器 macOS 界面](docs/images/app-macos.png)

> 所有媒体均在本机处理。桌面版无需账户、API Key 或云服务；手机 WebUI 仅用于可信局域网。

## 直接下载

| 你的电脑 | 安装包 |
|---|---|
| Windows 10/11 x64 | [下载 Windows 安装程序](https://github.com/PA5MIN/lora-frame-picker/releases/latest/download/LoRA-Frame-Picker-Windows-x64-Setup.exe) |
| Apple Silicon Mac（M1/M2/M3/M4/M5） | [下载 Apple Silicon DMG](https://github.com/PA5MIN/lora-frame-picker/releases/latest/download/LoRA-Frame-Picker-macOS-Apple-Silicon.dmg) |
| Intel Mac | [下载 Intel Mac DMG](https://github.com/PA5MIN/lora-frame-picker/releases/latest/download/LoRA-Frame-Picker-macOS-Intel.dmg) |

安装包已包含 Python 和全部运行依赖。下载后双击安装即可，无需配置开发环境。

## 你可以用它做什么

- 视频播放、时间轴定位、逐帧前后移动与 JPEG 导出
- 图片预览、常用比例裁剪、原图导出和批量去黑边
- 手机 WebUI：同一 Wi-Fi 内上传、预览和导出画面
- 源目录与导出目录防误用，自动避免重复扫描
- 本地处理，不需要账户、API Key 或云服务

## 安装方法

### Windows 安装

1. 双击下载的 `Setup.exe`。
2. 点击“安装”。安装程序默认安装到当前用户目录，不要求管理员权限。
3. 安装完成后直接启动；开始菜单中也会出现“LoRA Frame Picker”和“LoRA 手机 WebUI”。

### Mac 安装

1. 双击下载的 `.dmg`。
2. 把 `LoRA-Frame-Picker.app` 和需要使用的 `LoRA-Phone-WebUI.app` 拖到旁边的 `Applications`。
3. 以后从“应用程序”中双击启动。

首次打开时，系统可能显示安全提示：

- **Windows**：请确认安装包来自本项目的 GitHub Releases 页面，然后按系统提示选择“更多信息”→“仍要运行”。安装向导为英文，依次点击 **Next** 和 **Install** 即可。
- **macOS**：如果双击无法打开，请在 Finder 中按住 Control 点击 App，选择“打开”，再确认一次。

这些是首次启动时的系统提示，不影响软件在本地处理媒体。

## 可选：从源码运行

如果暂时没有与你电脑匹配的 Release，下载仓库 ZIP 并解压。首次运行需要联网安装依赖，之后可离线使用。

### Windows

1. 安装 [Python 3.9 或更高版本](https://www.python.org/downloads/windows/)，安装时勾选 `Add python.exe to PATH`。
2. 双击 `Start-LoRA-Frame-Picker.bat`。
3. 手机 WebUI 双击 `Start-LoRA-WebUI.bat`。

脚本会在项目内创建独立的 `.venv`，自动安装缺少的依赖，不会修改系统 Python 包。

### macOS

1. 安装 [Python 3.9 或更高版本](https://www.python.org/downloads/macos/)；建议使用 python.org 官方安装包。
2. 双击 `Start-LoRA-Frame-Picker.command`。
3. 手机 WebUI 双击 `Start-LoRA-WebUI.command`。

如果 `.command` 文件无法执行，在终端进入项目目录后运行：

```bash
chmod +x *.command
```

## 手机 WebUI

安装版从开始菜单或“应用程序”启动 `LoRA 手机 WebUI` 后，会自动打开电脑浏览器。页面顶部直接显示带临时访问口令的手机地址，不需要查看终端。手机和电脑必须连接同一个可信 Wi-Fi。

- 每次启动都会生成新的随机口令。
- 默认上传到“图片/LoRA Frame Picker/Uploads”。
- 默认导出到“图片/LoRA Frame Picker/Exports”。
- 源码版可双击 `Configure-LoRA-WebUI.command` 或 `Configure-LoRA-WebUI.bat` 更改目录。
- 单个上传文件上限为 12 GiB。
- 安装版用完后点击页面顶部“停止 WebUI”；源码版也可按 `Ctrl+C`。不要把服务直接暴露到互联网。

部分手机浏览器不能直接播放 MKV、AVI 或特殊编码视频，优先使用 MP4/MOV；其他格式可使用桌面版筛帧。

## 桌面版快捷键

| 快捷键 | 视频/媒体页 | 图片裁剪页 |
|---|---|---|
| `空格` | 播放/暂停 | 保存并切换下一张 |
| `←` / `→` | 前后逐帧 | 上一张/下一张 |
| `↑` / `↓` | 上一个/下一个媒体 | — |
| `S` | 保存当前画面 | 保存当前图片 |
| `1`–`8` | — | 切换裁剪尺寸 |
| `[` / `]` | — | 循环切换尺寸 |

请始终把媒体源目录与导出目录分开。程序会阻止两者完全相同，并在导出目录位于源目录内部时自动跳过该目录。

## 常见问题

### 提示找不到 Python

这一项只适用于从源码运行。请从 python.org 安装 Python 3.9 或更高版本。Windows 安装时勾选加入 PATH，然后重新双击启动脚本。

### 依赖安装失败

检查网络、代理和磁盘空间。删除项目中的 `.venv` 后重新运行启动脚本可重建环境；`.venv` 不包含个人媒体。

### 视频无法打开或没有画面

OpenCV 支持常见编码，但不保证支持所有容器和编码。先尝试 MP4（H.264）或 MOV；必要时用可信工具转码后再导入。

### WebUI 手机打不开

确认手机与电脑在同一 Wi-Fi、没有启用访客网络隔离，并允许程序通过系统防火墙。必须打开电脑页面顶部显示的完整链接，包括 `key=` 后的口令。

仍有问题或发现 Bug？请在 [Issues](https://github.com/PA5MIN/lora-frame-picker/issues) 中反馈，并附上操作系统版本、软件版本和报错信息；请勿上传私人媒体或密钥。

## 开发者与贡献者

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest
.venv/bin/python packaging/audit_release.py
```

推送 `v*` 标签后，GitHub Actions 会生成 Windows 图形安装程序，以及 macOS Apple Silicon/Intel 两个拖放安装 DMG。PyInstaller 不能跨系统构建，因此每个平台都在对应的 GitHub 托管运行器上打包。

### 提交代码时的隐私边界

仓库只包含程序源码、网页静态文件、测试、文档和构建配置。请勿提交：

- 人物图片、视频、数据集和导出结果
- LoRA/Checkpoint/ONNX 等模型文件
- HAR 网络记录、会话文件、配置、令牌、许可证或 `.env`
- 本机目录设置、缓存、虚拟环境和打包产物

发布前运行 `python packaging/audit_release.py`。详细说明见 [SECURITY.md](SECURITY.md)。

## 许可证

[MIT License](LICENSE)
