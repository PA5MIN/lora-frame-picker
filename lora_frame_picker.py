#!/usr/bin/env python3
"""LoRA 数据集筛帧器：从图片或视频中挑选清晰画面并导出。"""

from __future__ import annotations

import time
import tkinter as tk
import shutil
import os
import sys
import json
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import cv2
from PIL import Image, ImageOps, ImageTk


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def default_output_root() -> Path:
    """Return an expandable default that does not expose the account name in UI."""
    override = os.environ.get("LORA_FRAME_PICKER_OUTPUT_DIR")
    if override:
        return Path(override).expanduser()
    return Path("~") / "Pictures" / "LoRA Frame Picker"


if sys.platform == "win32":
    UI_FONT = "Microsoft YaHei UI"
elif sys.platform == "darwin":
    UI_FONT = "PingFang SC"
else:
    UI_FONT = "Noto Sans CJK SC"
CROP_PRESETS = {
    "9:16 竖图（常用） · 768 × 1376": (768, 1376),
    "16:9 横图（常用） · 1376 × 768": (1376, 768),
    "1:1 方图（常用） · 1024 × 1024": (1024, 1024),
    "4:3 横图 · 1184 × 896": (1184, 896),
    "3:2 横图 · 1248 × 832": (1248, 832),
    "2.35:1 超宽横图 · 1568 × 672": (1568, 672),
    "4:5 竖图 · 928 × 1152": (928, 1152),
    "2:3 竖图 · 832 × 1248": (832, 1248),
}

CROP_PRESETS_EN = {
    "9:16 Portrait (popular) · 768 × 1376": (768, 1376),
    "16:9 Landscape (popular) · 1376 × 768": (1376, 768),
    "1:1 Square (popular) · 1024 × 1024": (1024, 1024),
    "4:3 Landscape · 1184 × 896": (1184, 896),
    "3:2 Landscape · 1248 × 832": (1248, 832),
    "2.35:1 Ultrawide · 1568 × 672": (1568, 672),
    "4:5 Portrait · 928 × 1152": (928, 1152),
    "2:3 Portrait · 832 × 1248": (832, 1248),
}


TEXT = {
    "zh": {
        "app_title": "LoRA 数据集筛帧器", "subtitle": "视频筛帧 · 图片裁剪预览",
        "language": "语言", "tab_media": "视频 / 媒体筛帧", "tab_crop": "图片裁剪预览",
        "choose_media_folder": "选择媒体文件夹", "choose_media_files": "选择媒体文件",
        "choose_output": "选择导出目录", "media_list": "媒体列表    🔴 视频    🟢 图片",
        "no_media": "●  未加载媒体", "media_preview": "选择媒体文件夹后，在此预览画面",
        "previous": "◀ 上一个", "play": "▶ 播放", "pause": "⏸ 暂停", "next": "下一个 ▶",
        "save_frame": "保存当前画面  [S]", "choose_image_folder": "选择图片文件夹",
        "image_list": "图片列表", "crop_preview": "选择图片文件夹后，在此预览裁剪效果",
        "shortcuts": "空格：保存并下一张 · 1–8：切换尺寸 · [ / ]：循环尺寸",
        "previous_image": "◀ 上一张", "next_image": "下一张 ▶", "crop_ratio": "裁剪比例：",
        "use_original": "不裁剪，直接使用原图", "auto_black": "智能识别比例并去黑边",
        "batch_black": "批量自动去黑边", "save_next": "保存并下一张  [空格]",
        "no_media_status": "请选择包含图片或视频的文件夹", "unloaded_media": "未加载媒体", "unloaded_image": "未加载图片",
        "preset_hint": "快捷尺寸：1=9:16 · 2=16:9 · 3=1:1 · 4=4:3 · 5=3:2 · 6=2.35:1 · 7=4:5 · 8=2:3",
        "image_mode": "原图模式：导出时不裁剪", "video_signal": "●  视频媒体  ·  红灯：可连续保存多个视频帧",
        "image_signal": "●  图片媒体  ·  绿灯：保存后自动进入下一张",
        "select_image_folder": "选择包含图片的文件夹", "select_crop_output": "选择裁剪图片导出目录",
        "select_media_folder": "选择媒体文件夹", "select_media": "选择图片或视频", "media_files": "媒体文件", "all_files": "所有文件",
        "select_frame_output": "选择导出画面目录", "export_failed": "导出失败", "batch_failed": "批量处理失败",
        "save_failed": "保存失败", "output_unavailable": "导出目录不可用", "separate_folders": "请分开源目录和导出目录", "save_blocked": "已阻止保存",
        "no_images": "该文件夹中没有支持的图片文件", "loaded_images": "已载入 {count} 张图片", "read_image_failed": "无法读取图片：{error}",
        "no_export_image": "没有可导出的图片", "exported": "✓ 已导出：{name}（{width} × {height}）", "original_exported": "✓ 已原样导出：{name}",
        "choose_image_first": "请先选择图片文件夹", "loaded_media": "已载入 {count} 个媒体文件", "no_supported_media": "没有找到受支持的图片或视频文件",
        "no_frame": "没有可保存的画面", "video_open_failed": "无法打开视频：{name}", "image_read_failed": "无法读取图片：{error}",
        "video_status": "视频：{seconds:.1f} 秒，拖动进度条定位，S 保存画面", "image_position": "图片 · {width} × {height}", "image_status": "图片预览中，按 S 保存到导出目录",
        "frame_position": "{current} / {total}  ·  第 {frame} 帧", "selected_files": "已选择 {count} 个媒体文件",
    },
    "en": {
        "app_title": "LoRA Frame Picker", "subtitle": "Video frames · Image crop preview",
        "language": "Language", "tab_media": "Video / Media", "tab_crop": "Image crop preview",
        "choose_media_folder": "Choose media folder", "choose_media_files": "Choose media files",
        "choose_output": "Choose output folder", "media_list": "Media list    🔴 Video    🟢 Image",
        "no_media": "●  No media loaded", "media_preview": "Choose a media folder to preview it here",
        "previous": "◀ Previous", "play": "▶ Play", "pause": "⏸ Pause", "next": "Next ▶",
        "save_frame": "Save current frame  [S]", "choose_image_folder": "Choose image folder",
        "image_list": "Image list", "crop_preview": "Choose an image folder to preview the crop",
        "shortcuts": "Space: save & next · 1–8: crop preset · [ / ]: cycle presets",
        "previous_image": "◀ Previous", "next_image": "Next ▶", "crop_ratio": "Crop ratio:",
        "use_original": "Do not crop; use original image", "auto_black": "Detect ratio and remove black borders",
        "batch_black": "Remove black borders in batch", "save_next": "Save & next  [Space]",
        "no_media_status": "Choose a folder containing images or videos", "unloaded_media": "No media loaded", "unloaded_image": "No image loaded",
        "preset_hint": "Shortcuts: 1=9:16 · 2=16:9 · 3=1:1 · 4=4:3 · 5=3:2 · 6=2.35:1 · 7=4:5 · 8=2:3",
        "image_mode": "Original-image mode: export without cropping", "video_signal": "●  Video  ·  Red: save multiple frames from this video",
        "image_signal": "●  Image  ·  Green: move to the next image after saving",
        "select_image_folder": "Choose a folder containing images", "select_crop_output": "Choose crop output folder",
        "select_media_folder": "Choose media folder", "select_media": "Choose images or videos", "media_files": "Media files", "all_files": "All files",
        "select_frame_output": "Choose frame output folder", "export_failed": "Export failed", "batch_failed": "Batch processing failed",
        "save_failed": "Save failed", "output_unavailable": "Output folder unavailable", "separate_folders": "Keep source and output folders separate", "save_blocked": "Save blocked",
        "no_images": "No supported image files were found in this folder", "loaded_images": "Loaded {count} images", "read_image_failed": "Could not read image: {error}",
        "no_export_image": "There is no image to export", "exported": "✓ Exported: {name} ({width} × {height})", "original_exported": "✓ Exported original: {name}",
        "choose_image_first": "Choose an image folder first", "loaded_media": "Loaded {count} media files", "no_supported_media": "No supported image or video files were found",
        "no_frame": "There is no frame to save", "video_open_failed": "Could not open video: {name}", "image_read_failed": "Could not read image: {error}",
        "video_status": "Video: {seconds:.1f} sec · drag the timeline to seek · press S to save", "image_position": "Image · {width} × {height}", "image_status": "Previewing image · press S to save to the output folder",
        "frame_position": "{current} / {total}  ·  Frame {frame}", "selected_files": "Selected {count} media files",
    },
}


def settings_path() -> Path:
    """Return the per-user settings file; it is never stored in the project."""
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "LoRA Frame Picker" / "settings.json"


def load_language() -> str:
    try:
        language = json.loads(settings_path().read_text(encoding="utf-8")).get("language")
        return language if language in TEXT else "zh"
    except (OSError, ValueError, TypeError):
        return "zh"


def detect_black_border(image: Image.Image) -> tuple[int, int, int, int]:
    """检测图片四周连续的黑色/近黑色边框，返回 (left, top, right, bottom)。

    检测只看从边缘开始的连续区域，并要求整行/整列几乎都是黑色，
    因此不会因为画面中间有一块深色内容而误裁。
    """
    gray = image.convert("L")
    width, height = gray.size
    if width < 24 or height < 24:
        return (0, 0, width, height)

    # 缩小后检测足够快，同时对视频截图常见的压缩噪点更稳定。
    sample = gray.copy()
    sample.thumbnail((360, 360), Image.Resampling.BILINEAR)
    pixels = sample.load()
    sw, sh = sample.size
    threshold = 32
    dark_ratio = 0.985

    def row_is_border(y: int) -> bool:
        values = [pixels[x, y] for x in range(sw)]
        return sum(value <= threshold for value in values) / sw >= dark_ratio

    def col_is_border(x: int) -> bool:
        values = [pixels[x, y] for y in range(sh)]
        return sum(value <= threshold for value in values) / sh >= dark_ratio

    top = 0
    while top < sh // 2 and row_is_border(top):
        top += 1
    bottom = sh
    while bottom > sh // 2 and row_is_border(bottom - 1):
        bottom -= 1
    left = 0
    while left < sw // 2 and col_is_border(left):
        left += 1
    right = sw
    while right > sw // 2 and col_is_border(right - 1):
        right -= 1

    # 很薄的自然黑边不处理，避免误裁真实图片边缘。
    min_y = max(3, round(sh * 0.008))
    min_x = max(3, round(sw * 0.008))
    if top < min_y:
        top = 0
    if sh - bottom < min_y:
        bottom = sh
    if left < min_x:
        left = 0
    if sw - right < min_x:
        right = sw

    scale_x, scale_y = width / sw, height / sh
    box = (round(left * scale_x), round(top * scale_y),
           round(right * scale_x), round(bottom * scale_y))
    # 防止检测结果过小或坐标因缩放重合。
    if box[2] - box[0] < width * 0.35 or box[3] - box[1] < height * 0.35:
        return (0, 0, width, height)
    return box


COMMON_ASPECT_RATIOS = (
    ("9:16", 9 / 16),
    ("2:3", 2 / 3),
    ("3:4", 3 / 4),
    ("3:5", 3 / 5),
    ("5:7", 5 / 7),
    ("4:5", 4 / 5),
    ("1:1", 1.0),
    ("4:3", 4 / 3),
    ("3:2", 3 / 2),
)


def describe_aspect_ratio(width: int, height: int) -> str:
    """把检测到的实际比例标成最接近的常见比例，同时保留精确数值。"""
    if width <= 0 or height <= 0:
        return "未知比例"
    ratio = width / height
    name, target = min(COMMON_ASPECT_RATIOS, key=lambda item: abs(item[1] - ratio))
    # 只有接近常见比例时才贴标签，避免把任意照片误叫成某个标准比例。
    if abs(target - ratio) / target <= 0.025:
        return f"{name}（{width} × {height}）"
    return f"自定义比例 {ratio:.3f}（{width} × {height}）"


class FramePicker(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.language = load_language()
        self.title(self.t("app_title"))
        self.geometry("1420x900")
        self.minsize(1000, 680)
        self.configure(bg="#17191e")

        self.files: list[Path] = []
        self.media_source_root: Path | None = None
        self.index = -1
        self.cap: cv2.VideoCapture | None = None
        self.is_video = False
        self.playing = False
        self.duration_frames = 0
        self.fps = 25.0
        self.current_frame = 0
        self.current_image: Image.Image | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.preview_signal: tk.Label | None = None
        self.last_preview_size = (0, 0)
        output_root = default_output_root()
        self.output_dir = tk.StringVar(value=str(output_root / "Frames"))
        self.source_dir = tk.StringVar()
        self.status = tk.StringVar(value=self.t("no_media_status"))
        self.position_text = tk.StringVar(value="—")
        self.file_text = tk.StringVar(value=self.t("unloaded_media"))
        self._updating_scale = False
        self._save_count = 0

        self.crop_files: list[Path] = []
        self.crop_index = -1
        self.crop_image: Image.Image | None = None
        self.crop_photo: ImageTk.PhotoImage | None = None
        self.crop_display = (0.0, 0.0, 1.0, 1.0)
        self.crop_rect = (0.0, 0.0, 1.0, 1.0)
        self.crop_drag_mode: str | None = None
        self.crop_drag_start = (0.0, 0.0)
        self.crop_start_rect = (0.0, 0.0, 1.0, 1.0)
        self.crop_source_dir = tk.StringVar()
        self.crop_output_dir = tk.StringVar(value=str(output_root / "Crops"))
        self.crop_preset = tk.StringVar(value=next(iter(self._crop_presets())))
        self.crop_use_original = tk.BooleanVar(value=False)
        # 裁剪页默认先做比例/黑边识别，避免把视频画布比例误当成图片比例。
        self.crop_remove_black = tk.BooleanVar(value=True)
        self.crop_detected_box = (0, 0, 1, 1)
        self.crop_file_text = tk.StringVar(value=self.t("unloaded_image"))
        self.crop_status = tk.StringVar(value=self.t("preset_hint"))

        self._setup_style()
        self._build_ui()
        self._bind_keys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def t(self, key: str, **values: object) -> str:
        return TEXT[self.language][key].format(**values)

    def _crop_presets(self) -> dict[str, tuple[int, int]]:
        return CROP_PRESETS_EN if self.language == "en" else CROP_PRESETS

    def _language_label(self) -> str:
        return "English" if self.language == "en" else "中文"

    def _set_language(self, value: str) -> None:
        new_language = "en" if value == "English" else "zh"
        if new_language == self.language:
            return
        old_preset_index = list(self._crop_presets()).index(self.crop_preset.get())
        self.language = new_language
        self.crop_preset.set(list(self._crop_presets())[old_preset_index])
        try:
            path = settings_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"language": self.language}), encoding="utf-8")
        except OSError:
            pass
        self.title(self.t("app_title"))
        self._rebuild_ui()

    def _rebuild_ui(self) -> None:
        """Refresh visible labels immediately while keeping selected files and settings."""
        for child in self.winfo_children():
            child.destroy()
        self._build_ui()
        for path in self.files:
            signal = "🔴" if path.suffix.lower() in VIDEO_EXTENSIONS else "🟢"
            self.file_list.insert(tk.END, f"{signal}  {path.name}")
        if self.index >= 0:
            self.file_list.selection_set(self.index)
            self.file_list.see(self.index)
            self._set_preview_media_signal(self.is_video)
            self.render_image()
        for path in self.crop_files:
            self.crop_list.insert(tk.END, f"🖼  {path.name}")
        if self.crop_index >= 0:
            self.crop_list.selection_set(self.crop_index)
            self.crop_list.see(self.crop_index)
            self.render_crop_preview()

    def _setup_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#17191e", borderwidth=0, relief="flat",
                        bordercolor="#17191e", lightcolor="#17191e", darkcolor="#17191e")
        style.configure("Panel.TFrame", background="#20242c", borderwidth=0, relief="flat",
                        bordercolor="#20242c", lightcolor="#20242c", darkcolor="#20242c")
        style.configure("TLabel", background="#17191e", foreground="#e8edf3", font=(UI_FONT, 13))
        style.configure("Sub.TLabel", background="#20242c", foreground="#aeb8c6", font=(UI_FONT, 11))
        style.configure("Title.TLabel", background="#17191e", foreground="#ffffff", font=(UI_FONT, 20, "bold"))
        style.configure("TButton", background="#2f3745", foreground="#ffffff", padding=(11, 7), font=(UI_FONT, 12))
        style.map("TButton", background=[("active", "#455166")])
        style.configure("Accent.TButton", background="#3478f6", foreground="#ffffff", font=(UI_FONT, 12, "bold"))
        style.map("Accent.TButton", background=[("active", "#5791ff")])
        style.configure("TEntry", fieldbackground="#111318", background="#111318", foreground="#e8edf3",
                        insertcolor="#ffffff", bordercolor="#3b4350", lightcolor="#3b4350", darkcolor="#3b4350")
        style.configure("Horizontal.TScale", background="#20242c", troughcolor="#3b4350")
        style.configure("TCheckbutton", background="#20242c", foreground="#e8edf3", font=(UI_FONT, 11))
        style.map("TCheckbutton", background=[("active", "#20242c")], foreground=[("active", "#ffffff")])
        style.configure("Dark.Vertical.TScrollbar", background="#343b47", troughcolor="#171b21",
                        bordercolor="#171b21", arrowcolor="#aeb8c6", lightcolor="#343b47",
                        darkcolor="#343b47", relief="flat", borderwidth=0)
        style.map("Dark.Vertical.TScrollbar", background=[("active", "#4b5668"), ("pressed", "#5a6780")])
        style.configure("TCombobox", fieldbackground="#111318", background="#343b47", foreground="#e8edf3",
                        arrowcolor="#e8edf3", bordercolor="#3b4350", lightcolor="#3b4350", darkcolor="#3b4350")
        style.map("TCombobox", fieldbackground=[("readonly", "#111318")],
                  foreground=[("readonly", "#e8edf3")], background=[("readonly", "#343b47")])

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(22, 16, 22, 12))
        header.pack(fill="x")
        ttk.Label(header, text=self.t("app_title"), style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f"  {self.t('subtitle')}", style="TLabel").pack(side="left", padx=18)
        language = ttk.Frame(header)
        language.pack(side="right")
        ttk.Label(language, text=f"{self.t('language')}: ", style="Sub.TLabel").pack(side="left")
        self.language_selector = ttk.Combobox(language, values=("中文", "English"), state="readonly", width=9)
        self.language_selector.set(self._language_label())
        self.language_selector.bind("<<ComboboxSelected>>", lambda _event: self._set_language(self.language_selector.get()))
        self.language_selector.pack(side="left")

        # macOS 的 ttk.Notebook 在深色 clam 主题下会强制画一圈亮色客户区边框。
        # 自绘页签栏使三平台外观一致，同时避免视觉上的“白框”。
        tab_bar = tk.Frame(self, bg="#17191e", height=42, bd=0, highlightthickness=0)
        tab_bar.pack(fill="x", padx=16)
        self._tab_buttons: list[tk.Label] = []
        for index, label in enumerate((self.t("tab_media"), self.t("tab_crop"))):
            button = tk.Label(tab_bar, text=label, bg="#252a33", fg="#aeb8c6",
                              bd=0, relief="flat", highlightthickness=0,
                              padx=18, pady=9, font=(UI_FONT, 12), cursor="hand2")
            button.bind("<Button-1>", lambda _event, i=index: self._show_tab(i))
            button.bind("<Enter>", lambda _event, widget=button: self._set_tab_hover(widget, True))
            button.bind("<Leave>", lambda _event, widget=button: self._set_tab_hover(widget, False))
            button.pack(side="left", padx=(0, 2))
            self._tab_buttons.append(button)

        content_host = tk.Frame(self, bg="#17191e", bd=0, highlightthickness=0)
        content_host.pack(fill="both", expand=True)
        content_host.rowconfigure(0, weight=1)
        content_host.columnconfigure(0, weight=1)
        video_tab = tk.Frame(content_host, bg="#17191e", bd=0, relief="flat", highlightthickness=0)
        crop_tab = tk.Frame(content_host, bg="#17191e", bd=0, relief="flat", highlightthickness=0)
        video_tab.grid(row=0, column=0, sticky="nsew")
        crop_tab.grid(row=0, column=0, sticky="nsew")
        self._tab_pages = (video_tab, crop_tab)
        self._active_tab = 0

        path_bar = ttk.Frame(video_tab, style="Panel.TFrame", padding=12)
        path_bar.pack(fill="x", padx=18)
        ttk.Button(path_bar, text=self.t("choose_media_folder"), command=self.choose_source).grid(row=0, column=0, padx=(0, 9))
        ttk.Button(path_bar, text=self.t("choose_media_files"), command=self.choose_files).grid(row=0, column=1, padx=(0, 9))
        ttk.Entry(path_bar, textvariable=self.source_dir).grid(row=0, column=2, sticky="ew")
        ttk.Button(path_bar, text=self.t("choose_output"), command=self.choose_output).grid(row=0, column=3, padx=(9, 0))
        ttk.Entry(path_bar, textvariable=self.output_dir, width=32).grid(row=0, column=4, padx=(9, 0), sticky="ew")
        path_bar.columnconfigure(2, weight=3)
        path_bar.columnconfigure(4, weight=2)

        body = ttk.Frame(video_tab, padding=(18, 14, 18, 10))
        body.pack(fill="both", expand=True)
        sidebar = ttk.Frame(body, style="Panel.TFrame", padding=8, width=285)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text=self.t("media_list"), style="Sub.TLabel").pack(anchor="w", padx=4, pady=(2, 7))
        self.file_list = tk.Listbox(sidebar, bg="#171b21", fg="#dce3ed", selectbackground="#3478f6",
                                    selectforeground="#ffffff", borderwidth=0, highlightthickness=0,
                                    font=(UI_FONT, 12), activestyle="none")
        scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.file_list.yview,
                               style="Dark.Vertical.TScrollbar")
        self.file_list.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.file_list.pack(fill="both", expand=True)
        self.file_list.bind("<<ListboxSelect>>", self._on_select)

        main = ttk.Frame(body)
        main.pack(side="left", fill="both", expand=True, padx=(14, 0))
        signal_bar = tk.Frame(main, bg="#20242c", height=42)
        signal_bar.pack(fill="x", pady=(0, 8))
        signal_bar.pack_propagate(False)
        self.preview_signal = tk.Label(signal_bar, text=self.t("no_media"), bg="#20242c", fg="#8d97a6",
                                       anchor="w", padx=14, font=(UI_FONT, 15, "bold"))
        self.preview_signal.pack(fill="both", expand=True)
        self.preview_box = tk.Frame(main, bg="#08090b", highlightbackground="#353c48", highlightthickness=1)
        self.preview_box.pack(fill="both", expand=True)
        self.preview = tk.Label(self.preview_box, text=self.t("media_preview"), bg="#08090b", fg="#808b9a",
                                font=(UI_FONT, 17))
        self.preview.place(relx=.5, rely=.5, anchor="center")
        # 图片标签会随缩略图尺寸变化；只能监听外层预览区，避免缩略图被反复缩小。
        self.preview_box.bind("<Configure>", self._on_preview_resize)

        info = ttk.Frame(main, padding=(2, 10, 2, 4))
        info.pack(fill="x")
        ttk.Label(info, textvariable=self.file_text).pack(side="left")
        ttk.Label(info, textvariable=self.position_text).pack(side="right")

        controls = ttk.Frame(main, style="Panel.TFrame", padding=(13, 10))
        controls.pack(fill="x")
        ttk.Button(controls, text=self.t("previous"), command=self.previous_file).pack(side="left")
        self.play_button = ttk.Button(controls, text=self.t("play"), command=self.toggle_play)
        self.play_button.pack(side="left", padx=8)
        ttk.Button(controls, text=self.t("next"), command=self.next_file).pack(side="left")
        ttk.Button(controls, text=self.t("save_frame"), style="Accent.TButton", command=self.save_frame).pack(side="right")
        self.seek = ttk.Scale(controls, from_=0, to=1000, orient="horizontal", command=self.seek_to)
        self.seek.pack(side="left", fill="x", expand=True, padx=18)

        status = ttk.Frame(video_tab, style="Panel.TFrame", padding=(20, 8))
        status.pack(fill="x", side="bottom")
        ttk.Label(status, textvariable=self.status, style="Sub.TLabel").pack(side="left")

        self._build_crop_tab(crop_tab)
        self._show_tab(0)

    def _show_tab(self, index: int) -> None:
        self._active_tab = index
        self._tab_pages[index].tkraise()
        for button_index, button in enumerate(self._tab_buttons):
            selected = button_index == index
            button.configure(bg="#3478f6" if selected else "#252a33",
                             fg="#ffffff" if selected else "#aeb8c6")

    def _set_tab_hover(self, button: tk.Label, hovering: bool) -> None:
        index = self._tab_buttons.index(button)
        if index != self._active_tab:
            button.configure(bg="#313947" if hovering else "#252a33",
                             fg="#ffffff" if hovering else "#aeb8c6")

    def _build_crop_tab(self, parent: ttk.Frame) -> None:
        path_bar = ttk.Frame(parent, style="Panel.TFrame", padding=12)
        path_bar.pack(fill="x", padx=18, pady=(10, 0))
        ttk.Button(path_bar, text=self.t("choose_image_folder"), command=self.choose_crop_folder).grid(row=0, column=0, padx=(0, 9))
        ttk.Entry(path_bar, textvariable=self.crop_source_dir).grid(row=0, column=1, sticky="ew")
        ttk.Button(path_bar, text=self.t("choose_output"), command=self.choose_crop_output).grid(row=0, column=2, padx=(9, 0))
        ttk.Entry(path_bar, textvariable=self.crop_output_dir, width=32).grid(row=0, column=3, padx=(9, 0), sticky="ew")
        path_bar.columnconfigure(1, weight=3)
        path_bar.columnconfigure(3, weight=2)

        body = ttk.Frame(parent, padding=(18, 14, 18, 10))
        body.pack(fill="both", expand=True)
        sidebar = ttk.Frame(body, style="Panel.TFrame", padding=8, width=285)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text=self.t("image_list"), style="Sub.TLabel").pack(anchor="w", padx=4, pady=(2, 7))
        self.crop_list = tk.Listbox(sidebar, bg="#171b21", fg="#dce3ed", selectbackground="#3478f6",
                                    selectforeground="#ffffff", borderwidth=0, highlightthickness=0,
                                    font=(UI_FONT, 12), activestyle="none")
        crop_scroll = ttk.Scrollbar(sidebar, orient="vertical", command=self.crop_list.yview,
                                    style="Dark.Vertical.TScrollbar")
        self.crop_list.configure(yscrollcommand=crop_scroll.set)
        crop_scroll.pack(side="right", fill="y")
        self.crop_list.pack(fill="both", expand=True)
        self.crop_list.bind("<<ListboxSelect>>", self._on_crop_select)

        main = ttk.Frame(body)
        main.pack(side="left", fill="both", expand=True, padx=(14, 0))
        self.crop_canvas = tk.Canvas(main, bg="#08090b", highlightbackground="#353c48", highlightthickness=1,
                                     cursor="crosshair")
        self.crop_canvas.pack(fill="both", expand=True)
        self.crop_canvas.bind("<Configure>", lambda _e: self.render_crop_preview())
        self.crop_canvas.bind("<ButtonPress-1>", self.crop_mouse_down)
        self.crop_canvas.bind("<B1-Motion>", self.crop_mouse_move)
        self.crop_canvas.bind("<ButtonRelease-1>", self.crop_mouse_up)
        self.crop_canvas.bind("<MouseWheel>", self.crop_mouse_wheel)
        self.crop_canvas.bind("<Button-4>", lambda event: self.crop_mouse_wheel(event, 1))
        self.crop_canvas.bind("<Button-5>", lambda event: self.crop_mouse_wheel(event, -1))

        info = ttk.Frame(main, padding=(2, 10, 2, 4))
        info.pack(fill="x")
        ttk.Label(info, textvariable=self.crop_file_text).pack(side="left")
        ttk.Label(info, text=self.t("shortcuts"), style="Sub.TLabel").pack(side="right")

        controls = ttk.Frame(main, style="Panel.TFrame", padding=(13, 10))
        controls.pack(fill="x")
        ttk.Button(controls, text=self.t("previous_image"), command=lambda: self.change_crop_file(-1)).pack(side="left")
        ttk.Button(controls, text=self.t("next_image"), command=lambda: self.change_crop_file(1)).pack(side="left", padx=8)
        ttk.Label(controls, text=self.t("crop_ratio"), style="Sub.TLabel").pack(side="left", padx=(14, 2))
        preset = ttk.Combobox(controls, textvariable=self.crop_preset, values=list(self._crop_presets()), state="readonly", width=31)
        preset.pack(side="left")
        preset.bind("<<ComboboxSelected>>", lambda _e: self.reset_crop_rect())
        ttk.Checkbutton(controls, text=self.t("use_original"), variable=self.crop_use_original,
                        command=self.render_crop_preview).pack(side="left", padx=16)
        ttk.Checkbutton(controls, text=self.t("auto_black"), variable=self.crop_remove_black,
                        command=self.toggle_auto_black_crop).pack(side="left", padx=(0, 12))
        ttk.Button(controls, text=self.t("batch_black"), command=self.batch_remove_black).pack(side="left")
        ttk.Button(controls, text=self.t("save_next"), style="Accent.TButton",
                   command=self.export_crop_and_next).pack(side="right")

        status = ttk.Frame(parent, style="Panel.TFrame", padding=(20, 8))
        status.pack(fill="x", side="bottom")
        ttk.Label(status, textvariable=self.crop_status, style="Sub.TLabel").pack(side="left")

    def _bind_keys(self) -> None:
        self.bind_all("<space>", self._handle_space)
        self.bind_all("<Left>", self._handle_left)
        self.bind_all("<Right>", self._handle_right)
        self.bind_all("<Up>", self._handle_up)
        self.bind_all("<Down>", self._handle_down)
        self.bind_all("s", self._handle_save)
        self.bind_all("S", self._handle_save)
        for index in range(len(self._crop_presets())):
            self.bind_all(str(index + 1), lambda event, i=index: self._handle_preset_shortcut(event, i))
        self.bind_all("[", lambda event: self._handle_preset_cycle(event, -1))
        self.bind_all("]", lambda event: self._handle_preset_cycle(event, 1))

    def _on_crop_tab(self) -> bool:
        return self._active_tab == 1

    def _handle_space(self, _event: tk.Event) -> str | None:
        if self._on_crop_tab():
            self.export_crop_and_next()
            return "break"
        self.toggle_play()
        return "break"

    def _handle_left(self, _event: tk.Event) -> None:
        if self._on_crop_tab():
            self.change_crop_file(-1)
        else:
            self.step(-1)

    def _handle_right(self, _event: tk.Event) -> None:
        if self._on_crop_tab():
            self.change_crop_file(1)
        else:
            self.step(1)

    def _handle_up(self, _event: tk.Event) -> None:
        if not self._on_crop_tab():
            self.previous_file()

    def _handle_down(self, _event: tk.Event) -> None:
        if not self._on_crop_tab():
            self.next_file()

    def _handle_save(self, _event: tk.Event) -> None:
        if self._on_crop_tab():
            self.export_crop()
        else:
            self.save_frame()

    def _shortcut_is_typing(self) -> bool:
        focused = self.focus_get()
        return bool(focused and focused.winfo_class() in {"Entry", "TEntry", "TCombobox"})

    def _handle_preset_shortcut(self, _event: tk.Event, index: int) -> str | None:
        if not self._on_crop_tab() or self._shortcut_is_typing():
            return None
        presets = list(self._crop_presets())
        if 0 <= index < len(presets):
            self.crop_preset.set(presets[index])
            self.reset_crop_rect()
            self.crop_status.set(f"已切换裁剪尺寸：{index + 1} · {presets[index]}")
        return "break"

    def _handle_preset_cycle(self, _event: tk.Event, offset: int) -> str | None:
        if not self._on_crop_tab() or self._shortcut_is_typing():
            return None
        presets = list(self._crop_presets())
        current = presets.index(self.crop_preset.get())
        target = (current + offset) % len(presets)
        self.crop_preset.set(presets[target])
        self.reset_crop_rect()
        self.crop_status.set(f"已切换裁剪尺寸：{target + 1} · {presets[target]}")
        return "break"

    # ---- 图片裁剪页 -------------------------------------------------
    def choose_crop_folder(self) -> None:
        folder = filedialog.askdirectory(title=self.t("select_image_folder"))
        if not folder:
            return
        root = Path(folder)
        self.crop_source_dir.set(str(root))
        self.crop_files = sorted((p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS),
                                 key=lambda p: str(p).lower())
        self.crop_list.delete(0, tk.END)
        for path in self.crop_files:
            self.crop_list.insert(tk.END, f"🖼  {path.name}")
        if not self.crop_files:
            self.crop_index = -1
            self.crop_image = None
            self.crop_canvas.delete("all")
            self.crop_status.set(self.t("no_images"))
            return
        self.crop_status.set(self.t("loaded_images", count=len(self.crop_files)))
        self.open_crop_file(0)

    def choose_crop_output(self) -> None:
        folder = filedialog.askdirectory(title=self.t("select_crop_output"))
        if folder:
            self.crop_output_dir.set(folder)

    def _on_crop_select(self, _event: tk.Event) -> None:
        selected = self.crop_list.curselection()
        if selected and selected[0] != self.crop_index:
            self.open_crop_file(selected[0])

    def change_crop_file(self, offset: int) -> None:
        if self.crop_files:
            self.open_crop_file((self.crop_index + offset) % len(self.crop_files))

    def open_crop_file(self, index: int) -> None:
        if not (0 <= index < len(self.crop_files)):
            return
        try:
            with Image.open(self.crop_files[index]) as image:
                self.crop_image = ImageOps.exif_transpose(image).convert("RGB")
        except Exception as exc:
            self.crop_status.set(self.t("read_image_failed", error=exc))
            return
        self.crop_index = index
        self.crop_list.selection_clear(0, tk.END)
        self.crop_list.selection_set(index)
        self.crop_list.see(index)
        self.crop_file_text.set(f"{index + 1}/{len(self.crop_files)}  ·  {self.crop_files[index].name}  ·  {self.crop_image.width} × {self.crop_image.height}")
        self.crop_detected_box = detect_black_border(self.crop_image)
        detected_w = self.crop_detected_box[2] - self.crop_detected_box[0]
        detected_h = self.crop_detected_box[3] - self.crop_detected_box[1]
        detected_label = describe_aspect_ratio(detected_w, detected_h)
        has_border = self.crop_detected_box != (0, 0, self.crop_image.width, self.crop_image.height)
        border_note = "，已发现黑边" if has_border else "，未发现连续黑边"
        self.crop_status.set(f"智能识别：{detected_label}{border_note}")
        self.reset_crop_rect()

    def _crop_ratio(self) -> float:
        width, height = self._crop_presets()[self.crop_preset.get()]
        return width / height

    def reset_crop_rect(self) -> None:
        """让当前比例的裁剪框以最大尺寸居中放进原图。"""
        if not self.crop_image:
            return
        if self.crop_remove_black.get():
            left, top, right, bottom = self.crop_detected_box
            self.crop_rect = (left, top, right - left, bottom - top)
            self.render_crop_preview()
            return
        image_w, image_h = self.crop_image.size
        ratio = self._crop_ratio()
        if image_w / image_h > ratio:
            height = image_h
            width = height * ratio
        else:
            width = image_w
            height = width / ratio
        self.crop_rect = ((image_w - width) / 2, (image_h - height) / 2, width, height)
        self.render_crop_preview()

    def toggle_auto_black_crop(self) -> None:
        """切换自动去黑边；自动模式保留检测出的原始图片比例。"""
        if self.crop_remove_black.get():
            self.crop_status.set("已启用自动去黑边：仅裁掉四周连续黑色边框")
        else:
            self.crop_status.set("已关闭自动去黑边：恢复所选固定比例裁剪")
        self.reset_crop_rect()

    def _crop_box(self) -> tuple[int, int, int, int]:
        if self.crop_remove_black.get():
            return tuple(round(value) for value in self.crop_detected_box)
        x, y, width, height = self.crop_rect
        return (round(x), round(y), round(x + width), round(y + height))

    def render_crop_preview(self) -> None:
        if not hasattr(self, "crop_canvas"):
            return
        canvas = self.crop_canvas
        canvas.delete("all")
        if not self.crop_image:
            canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2, text=self.t("crop_preview"),
                               fill="#808b9a", font=(UI_FONT, 17))
            return
        canvas_w, canvas_h = canvas.winfo_width(), canvas.winfo_height()
        if canvas_w < 30 or canvas_h < 30:
            return
        image_w, image_h = self.crop_image.size
        scale = min((canvas_w - 20) / image_w, (canvas_h - 20) / image_h)
        shown_w, shown_h = image_w * scale, image_h * scale
        left, top = (canvas_w - shown_w) / 2, (canvas_h - shown_h) / 2
        preview = self.crop_image.copy()
        preview.thumbnail((round(shown_w), round(shown_h)), Image.Resampling.LANCZOS)
        self.crop_photo = ImageTk.PhotoImage(preview)
        canvas.create_image(left, top, image=self.crop_photo, anchor="nw")
        self.crop_display = (left, top, scale, scale)
        if self.crop_use_original.get():
            canvas.create_text(left + 12, top + 12, text=self.t("image_mode"), anchor="nw", fill="#ffffff",
                               font=(UI_FONT, 13, "bold"))
            return
        x, y, width, height = self.crop_rect
        x1, y1 = left + x * scale, top + y * scale
        x2, y2 = x1 + width * scale, y1 + height * scale
        # 半透明遮罩在 Tk Canvas 各平台表现不一致，使用深色点阵遮罩以保持清晰可见。
        for box in ((left, top, left + shown_w, y1), (left, y2, left + shown_w, top + shown_h),
                    (left, y1, x1, y2), (x2, y1, left + shown_w, y2)):
            canvas.create_rectangle(*box, fill="#000000", stipple="gray50", outline="")
        canvas.create_rectangle(x1, y1, x2, y2, outline="#ffffff", width=2)
        for fraction in (1 / 3, 2 / 3):
            canvas.create_line(x1 + (x2 - x1) * fraction, y1, x1 + (x2 - x1) * fraction, y2, fill="#ffffff", stipple="gray50")
            canvas.create_line(x1, y1 + (y2 - y1) * fraction, x2, y1 + (y2 - y1) * fraction, fill="#ffffff", stipple="gray50")
        for cx, cy in ((x1, y1), (x2, y1), (x1, y2), (x2, y2)):
            canvas.create_rectangle(cx - 6, cy - 6, cx + 6, cy + 6, fill="#ffffff", outline="#1e72ed", width=2)

    def _canvas_to_image(self, event: tk.Event) -> tuple[float, float]:
        left, top, scale, _ = self.crop_display
        assert self.crop_image
        return (max(0, min(self.crop_image.width, (event.x - left) / scale)),
                max(0, min(self.crop_image.height, (event.y - top) / scale)))

    def crop_mouse_down(self, event: tk.Event) -> None:
        if not self.crop_image or self.crop_use_original.get():
            return
        x, y, width, height = self.crop_rect
        px, py = self._canvas_to_image(event)
        handle = 18 / self.crop_display[2]
        corners = {"nw": (x, y), "ne": (x + width, y), "sw": (x, y + height), "se": (x + width, y + height)}
        self.crop_drag_mode = next((name for name, (cx, cy) in corners.items() if abs(px - cx) <= handle and abs(py - cy) <= handle), None)
        if not self.crop_drag_mode and x <= px <= x + width and y <= py <= y + height:
            self.crop_drag_mode = "move"
        if self.crop_drag_mode:
            self.crop_drag_start = (px, py)
            self.crop_start_rect = self.crop_rect

    def crop_mouse_move(self, event: tk.Event) -> None:
        if not self.crop_image or not self.crop_drag_mode:
            return
        px, py = self._canvas_to_image(event)
        x, y, width, height = self.crop_start_rect
        start_x, start_y = self.crop_drag_start
        image_w, image_h = self.crop_image.size
        if self.crop_drag_mode == "move":
            new_x = max(0, min(image_w - width, x + px - start_x))
            new_y = max(0, min(image_h - height, y + py - start_y))
            self.crop_rect = (new_x, new_y, width, height)
        else:
            mode = self.crop_drag_mode
            anchor_x = x + width if "w" in mode else x
            anchor_y = y + height if "n" in mode else y
            max_width = anchor_x if "w" in mode else image_w - anchor_x
            max_height = anchor_y if "n" in mode else image_h - anchor_y
            desired_w, desired_h = abs(px - anchor_x), abs(py - anchor_y)
            ratio = self._crop_ratio()
            if desired_h == 0 or desired_w / desired_h > ratio:
                new_width = desired_w
                new_height = new_width / ratio
            else:
                new_height = desired_h
                new_width = new_height * ratio
            new_width = max(32, min(new_width, max_width, max_height * ratio))
            new_height = new_width / ratio
            new_x = anchor_x - new_width if "w" in mode else anchor_x
            new_y = anchor_y - new_height if "n" in mode else anchor_y
            self.crop_rect = (new_x, new_y, new_width, new_height)
        self.render_crop_preview()

    def crop_mouse_up(self, _event: tk.Event) -> None:
        self.crop_drag_mode = None

    def crop_mouse_wheel(self, event: tk.Event, direction: int | None = None) -> str:
        """围绕鼠标位置缩放取景范围；向上滚动等同于放大图片。"""
        if not self.crop_image or self.crop_use_original.get():
            return "break"
        if direction is None:
            direction = 1 if event.delta > 0 else -1
        x, y, width, height = self.crop_rect
        pointer_x, pointer_y = self._canvas_to_image(event)
        ratio = self._crop_ratio()
        image_w, image_h = self.crop_image.size

        # 缩小裁剪区域会让内容在最终输出中显得更大，反之则缩小。
        factor = 0.88 if direction > 0 else 1 / 0.88
        max_width = min(float(image_w), float(image_h) * ratio)
        min_width = max(32.0, 32.0 * ratio)
        new_width = max(min_width, min(max_width, width * factor))
        new_height = new_width / ratio

        # 保持鼠标指向的画面位置在缩放前后尽量不动。
        relative_x = max(0.0, min(1.0, (pointer_x - x) / width))
        relative_y = max(0.0, min(1.0, (pointer_y - y) / height))
        new_x = pointer_x - relative_x * new_width
        new_y = pointer_y - relative_y * new_height
        new_x = max(0.0, min(image_w - new_width, new_x))
        new_y = max(0.0, min(image_h - new_height, new_y))
        self.crop_rect = (new_x, new_y, new_width, new_height)
        self.render_crop_preview()
        self.crop_status.set("滚轮向上放大、向下缩小；裁剪比例保持不变")
        return "break"

    def export_crop_and_next(self) -> None:
        if self.export_crop():
            self.change_crop_file(1)

    def export_crop(self) -> bool:
        if not self.crop_image or self.crop_index < 0:
            self.crop_status.set(self.t("no_export_image"))
            return False
        try:
            output = Path(self.crop_output_dir.get()).expanduser()
            output.mkdir(parents=True, exist_ok=True)
            source = self.crop_files[self.crop_index]
            if self.crop_use_original.get():
                target = self._unique_path(output / source.name)
                shutil.copy2(source, target)
                self.crop_status.set(self.t("original_exported", name=target.name))
                return True
            cropped = self.crop_image.crop(self._crop_box())
            if self.crop_remove_black.get():
                target_w, target_h = cropped.size
                label = "去黑边"
            else:
                target_w, target_h = self._crop_presets()[self.crop_preset.get()]
                cropped = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
                label = self.crop_preset.get().split()[0].replace(":", "x")
            target = self._unique_path(output / f"{source.stem}_{label}.jpg")
            cropped.save(target, "JPEG", quality=95, subsampling=0)
            self.crop_status.set(self.t("exported", name=target.name, width=target_w, height=target_h))
            return True
        except Exception as exc:
            messagebox.showerror(self.t("export_failed"), str(exc))
            return False

    def batch_remove_black(self) -> None:
        """把当前图片文件夹中的图片批量裁掉四周连续黑边。"""
        if not self.crop_files:
            self.crop_status.set(self.t("choose_image_first"))
            return
        output = Path(self.crop_output_dir.get()).expanduser()
        try:
            output.mkdir(parents=True, exist_ok=True)
            saved = 0
            skipped = 0
            for source in self.crop_files:
                with Image.open(source) as image:
                    image = ImageOps.exif_transpose(image).convert("RGB")
                    box = detect_black_border(image)
                    if box == (0, 0, image.width, image.height):
                        skipped += 1
                        continue
                    cropped = image.crop(box)
                    ratio_label = describe_aspect_ratio(cropped.width, cropped.height).split("（")[0]
                    target = self._unique_path(output / f"{source.stem}_去黑边_{ratio_label}.jpg")
                    cropped.save(target, "JPEG", quality=95, subsampling=0)
                    saved += 1
            self.crop_status.set(f"✓ 批量完成：裁掉黑边 {saved} 张，未检测到黑边 {skipped} 张")
            if saved:
                self.open_crop_file(self.crop_index if self.crop_index >= 0 else 0)
        except Exception as exc:
            messagebox.showerror(self.t("batch_failed"), str(exc))

    def choose_source(self) -> None:
        folder = filedialog.askdirectory(title=self.t("select_media_folder"))
        if folder:
            self.load_folder(Path(folder))

    def choose_files(self) -> None:
        chosen = filedialog.askopenfilenames(
            title=self.t("select_media"),
            filetypes=[(self.t("media_files"), "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff *.mp4 *.mov *.mkv *.avi *.webm *.m4v *.flv"),
                       (self.t("all_files"), "*.*")],
        )
        if not chosen:
            return
        self.stop_playback()
        self.release_video()
        # 多选文件没有统一的源目录，不应用文件夹扫描的导出目录规则。
        self.media_source_root = None
        self.files = [Path(p) for p in chosen if Path(p).suffix.lower() in MEDIA_EXTENSIONS]
        self.source_dir.set(self.t("selected_files", count=len(self.files)))
        self.file_list.delete(0, tk.END)
        for p in self.files:
            signal = "🔴" if p.suffix.lower() in VIDEO_EXTENSIONS else "🟢"
            self.file_list.insert(tk.END, f"{signal}  {p.name}")
        if self.files:
            self.status.set(self.t("loaded_media", count=len(self.files)))
            self.open_file(0)

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(title=self.t("select_frame_output"))
        if folder:
            output = Path(folder).expanduser().resolve()
            if self.media_source_root and output == self.media_source_root:
                messagebox.showwarning("导出目录不可用", "导出目录不能与媒体源文件夹相同，否则导出的图片会被再次扫描并造成重复。\n\n请选择一个单独的导出文件夹。")
                return
            self.output_dir.set(str(output))
            # 输出目录位于媒体源内部时，重新扫描并自动排除该子目录。
            if self.media_source_root and self._is_inside(output, self.media_source_root):
                self.load_folder(self.media_source_root)

    def load_folder(self, folder: Path) -> None:
        self.stop_playback()
        self.release_video()
        folder = folder.expanduser().resolve()
        output = Path(self.output_dir.get()).expanduser().resolve()
        if output == folder:
            self.files = []
            self.file_list.delete(0, tk.END)
            self.media_source_root = None
            self.status.set("导出目录与媒体源相同：为避免重复，请选择单独的导出目录后再载入媒体")
            messagebox.showwarning("请分开源目录和导出目录", "导出目录不能与媒体源文件夹相同。\n\n否则保存的图片会被当成新媒体再次筛选，形成重复文件。")
            return
        self.media_source_root = folder
        self.source_dir.set(str(folder))
        # 若导出目录在源目录下，跳过它，防止历史导出文件进入待筛选列表。
        excluded = output if self._is_inside(output, folder) else None
        self.files = sorted((p for p in folder.rglob("*") if p.is_file()
                             and p.suffix.lower() in MEDIA_EXTENSIONS
                             and not (excluded and self._is_inside(p, excluded))),
                            key=lambda p: str(p).lower())
        self.file_list.delete(0, tk.END)
        for p in self.files:
            signal = "🔴" if p.suffix.lower() in VIDEO_EXTENSIONS else "🟢"
            self.file_list.insert(tk.END, f"{signal}  {p.name}")
        if not self.files:
            self.index = -1
            self.status.set(self.t("no_supported_media"))
            return
        self.status.set(self.t("loaded_media", count=len(self.files)))
        self.open_file(0)

    @staticmethod
    def _is_inside(path: Path, folder: Path) -> bool:
        """path 是否是 folder 本身或其任意子路径（路径均已规范化）。"""
        try:
            path.resolve().relative_to(folder.resolve())
            return True
        except ValueError:
            return False

    def _on_select(self, _event: tk.Event) -> None:
        selected = self.file_list.curselection()
        if selected and selected[0] != self.index:
            self.open_file(selected[0])

    def open_file(self, index: int) -> None:
        if not (0 <= index < len(self.files)):
            return
        self.stop_playback()
        self.release_video()
        self.index = index
        self.file_list.selection_clear(0, tk.END)
        self.file_list.selection_set(index)
        self.file_list.see(index)
        path = self.files[index]
        self.is_video = path.suffix.lower() in VIDEO_EXTENSIONS
        self._set_preview_media_signal(self.is_video)
        self.file_text.set(f"{index + 1}/{len(self.files)}  ·  {path.name}")
        if self.is_video:
            self.cap = cv2.VideoCapture(str(path))
            if not self.cap.isOpened():
                self.status.set(self.t("video_open_failed", name=path.name))
                return
            self.duration_frames = max(1, int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
            self.current_frame = 0
            self.show_video_frame(0)
            self.status.set(self.t("video_status", seconds=self.duration_frames / self.fps))
        else:
            try:
                with Image.open(path) as im:
                    self.current_image = ImageOps.exif_transpose(im).convert("RGB")
                self.duration_frames = 1
                self.current_frame = 0
                self.render_image()
                self.position_text.set(self.t("image_position", width=self.current_image.width, height=self.current_image.height))
                self.status.set(self.t("image_status"))
            except Exception as exc:
                self.status.set(self.t("image_read_failed", error=exc))

    def _set_preview_media_signal(self, is_video: bool) -> None:
        """在预览窗口正上方显示当前媒体类型，方便快速筛选。"""
        if not self.preview_signal:
            return
        if is_video:
            self.preview_signal.configure(text=self.t("video_signal"), fg="#ff5b61")
        else:
            self.preview_signal.configure(text=self.t("image_signal"), fg="#39d96b")

    def show_video_frame(self, frame: int) -> None:
        if not self.cap:
            return
        frame = max(0, min(frame, self.duration_frames - 1))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ok, bgr = self.cap.read()
        if not ok:
            return
        self.current_frame = frame
        self.current_image = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        self.render_image()
        seconds = frame / self.fps
        total = self.duration_frames / self.fps
        self.position_text.set(self.t("frame_position", current=self._format_time(seconds), total=self._format_time(total), frame=frame + 1))
        self._updating_scale = True
        self.seek.set(frame / max(1, self.duration_frames - 1) * 1000)
        self._updating_scale = False

    def render_image(self) -> None:
        if not self.current_image:
            return
        # 以固定的预览容器为基准，而不是以会随着图片缩放的 Label 为基准。
        w, h = self.preview_box.winfo_width(), self.preview_box.winfo_height()
        if w < 30 or h < 30:
            self.after(80, self.render_image)
            return
        image = self.current_image.copy()
        image.thumbnail((w - 12, h - 12), Image.Resampling.LANCZOS)
        self.preview_photo = ImageTk.PhotoImage(image)
        self.preview.configure(image=self.preview_photo, text="")
        self.preview.place(relx=.5, rely=.5, anchor="center")

    def _on_preview_resize(self, _event: tk.Event) -> None:
        if self.current_image:
            self.after_idle(self.render_image)

    def seek_to(self, value: str) -> None:
        if self._updating_scale or not self.is_video or not self.cap:
            return
        self.stop_playback()
        frame = round(float(value) / 1000 * (self.duration_frames - 1))
        self.show_video_frame(frame)

    def step(self, amount: int) -> None:
        if self.is_video and self.cap:
            self.stop_playback()
            self.show_video_frame(self.current_frame + amount)

    def previous_file(self) -> None:
        if self.files:
            self.open_file((self.index - 1) % len(self.files))

    def next_file(self) -> None:
        if self.files:
            self.open_file((self.index + 1) % len(self.files))

    def toggle_play(self) -> None:
        if not self.is_video or not self.cap:
            return
        self.playing = not self.playing
        self.play_button.configure(text=self.t("pause") if self.playing else self.t("play"))
        if self.playing:
            self._play_next()

    def _play_next(self) -> None:
        if not self.playing or not self.cap:
            return
        if self.current_frame >= self.duration_frames - 1:
            self.stop_playback()
            return
        start = time.monotonic()
        self.show_video_frame(self.current_frame + 1)
        delay = max(1, round(1000 / self.fps - (time.monotonic() - start) * 1000))
        self.after(delay, self._play_next)

    def stop_playback(self) -> None:
        self.playing = False
        if hasattr(self, "play_button"):
            self.play_button.configure(text=self.t("play"))

    def save_frame(self) -> None:
        if not self.current_image or self.index < 0:
            self.status.set(self.t("no_frame"))
            return
        try:
            output = Path(self.output_dir.get()).expanduser()
            if self.media_source_root and output.resolve() == self.media_source_root:
                messagebox.showwarning("已阻止保存", "导出目录与媒体源相同会造成循环重复。请先选择单独的导出目录。")
                return
            output.mkdir(parents=True, exist_ok=True)
            source = self.files[self.index].stem
            if self.is_video:
                name = f"{source}_frame_{self.current_frame:06d}.jpg"
            else:
                name = f"{source}.jpg"
            target = self._unique_path(output / name)
            self.current_image.save(target, "JPEG", quality=95, subsampling=0)
            self._save_count += 1
            saved_message = f"✓ 已保存：{target.name}（本次 {self._save_count} 张）"
            if self.is_video:
                # 一个视频通常需要连续挑选多帧，因此保存后停留在当前视频。
                self.status.set(saved_message + " · 仍停留在当前视频")
            else:
                # 图片通常一张只取一次，保存成功后直接进入下一个媒体。
                self.next_file()
                self.status.set(saved_message + " · 已自动进入下一个媒体")
        except Exception as exc:
            messagebox.showerror(self.t("save_failed"), str(exc))

    @staticmethod
    def _unique_path(path: Path) -> Path:
        if not path.exists():
            return path
        for n in range(2, 10000):
            candidate = path.with_stem(f"{path.stem}_{n}")
            if not candidate.exists():
                return candidate
        raise RuntimeError("无法创建不重复的文件名")

    @staticmethod
    def _format_time(seconds: float) -> str:
        minutes, sec = divmod(int(seconds), 60)
        return f"{minutes:02d}:{sec:02d}"

    def release_video(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None

    def _on_close(self) -> None:
        self.stop_playback()
        self.release_video()
        self.destroy()


if __name__ == "__main__":
    FramePicker().mainloop()
