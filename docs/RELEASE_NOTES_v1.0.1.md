# v1.0.1

## 中文

- 修复 Windows CI 中默认目录脱敏测试对路径分隔符的误判。
- WebUI 中的主目录路径在 Windows、macOS 和 Linux 上统一显示为 `~/...`。
- 不改变实际文件保存位置或路径处理方式。

## English

- Fixed a Windows CI false failure caused by assuming Unix path separators in a privacy test.
- Standardized home-directory display as `~/...` in WebUI responses on Windows, macOS, and Linux.
- Actual filesystem locations and platform-native path handling are unchanged.
