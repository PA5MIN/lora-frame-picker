import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from lora_frame_picker import default_output_root, describe_aspect_ratio, detect_black_border


class DesktopHelperTests(unittest.TestCase):
    def test_detect_black_border_removes_continuous_edge(self):
        image = Image.new("RGB", (200, 300), "black")
        content = Image.new("RGB", (160, 240), "white")
        image.paste(content, (20, 30))
        self.assertEqual(detect_black_border(image), (20, 30, 180, 270))

    def test_detect_black_border_keeps_normal_image(self):
        image = Image.new("RGB", (120, 80), "white")
        self.assertEqual(detect_black_border(image), (0, 0, 120, 80))

    def test_aspect_ratio_description(self):
        self.assertTrue(describe_aspect_ratio(1080, 1920).startswith("9:16"))

    def test_default_output_can_be_overridden(self):
        with tempfile.TemporaryDirectory() as temporary:
            override = Path(temporary) / "exports"
            with patch.dict(os.environ, {"LORA_FRAME_PICKER_OUTPUT_DIR": str(override)}):
                self.assertEqual(default_output_root(), override)

    def test_default_output_does_not_display_account_name(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(str(default_output_root()).startswith("~/"))


if __name__ == "__main__":
    unittest.main()
