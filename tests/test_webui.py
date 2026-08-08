import base64
import io
import tempfile
import unittest
from pathlib import Path

import lora_frame_picker_web as web


class WebUITests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.original_upload = web.UPLOAD_DIR
        self.original_export = web.EXPORT_DIR
        web.UPLOAD_DIR = root / "uploads"
        web.EXPORT_DIR = root / "exports"
        web.app.config.update(TESTING=True)
        self.client = web.app.test_client()

    def tearDown(self):
        web.UPLOAD_DIR = self.original_upload
        web.EXPORT_DIR = self.original_export
        self.temporary.cleanup()

    @staticmethod
    def auth_headers():
        return {"X-Lora-Key": web.ACCESS_KEY}

    def test_health_is_public_and_hardened(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"ok": True})
        self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

    def test_private_api_requires_key(self):
        self.assertEqual(self.client.get("/api/media").status_code, 403)

    def test_server_info_requires_key(self):
        self.assertEqual(self.client.get("/api/server-info").status_code, 403)
        response = self.client.get("/api/server-info", headers=self.auth_headers())
        self.assertEqual(response.status_code, 200)
        self.assertIn("urls", response.get_json())

    def test_upload_rejects_unsupported_file(self):
        response = self.client.post(
            "/api/upload",
            headers=self.auth_headers(),
            data={"files": (io.BytesIO(b"text"), "notes.txt")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)

    def test_upload_and_export_use_separate_directories(self):
        response = self.client.post(
            "/api/upload",
            headers=self.auth_headers(),
            data={"files": (io.BytesIO(b"fake image"), "sample.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue((web.UPLOAD_DIR / "sample.jpg").exists())

        encoded = base64.b64encode(b"fake jpeg bytes").decode("ascii")
        response = self.client.post(
            "/api/export",
            headers=self.auth_headers(),
            json={"image": f"data:image/jpeg;base64,{encoded}", "sourceName": "sample.jpg"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(web.EXPORT_DIR.glob("sample-*.jpg"))), 1)

    def test_unicode_filename_is_preserved_safely(self):
        response = self.client.post(
            "/api/upload",
            headers=self.auth_headers(),
            data={"files": (io.BytesIO(b"fake image"), "训练图片.jpg")},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue((web.UPLOAD_DIR / "训练图片.jpg").exists())

    def test_reserved_windows_name_is_prefixed(self):
        self.assertEqual(web.safe_media_filename("CON.jpg"), "_CON.jpg")

    def test_only_rfc1918_addresses_are_shown_to_phone_users(self):
        self.assertTrue(web.is_lan_address("192.168.31.146"))
        self.assertTrue(web.is_lan_address("10.0.0.8"))
        self.assertFalse(web.is_lan_address("198.18.0.1"))
        self.assertFalse(web.is_lan_address("127.0.0.1"))

    def test_home_path_is_redacted_for_display(self):
        displayed = web.display_path(Path.home() / "Pictures" / "LoRA Frame Picker")
        self.assertTrue(displayed.startswith("~/"))
        self.assertNotIn(Path.home().name, displayed)

    def test_media_path_traversal_is_rejected(self):
        response = self.client.get("/media/..%2Fprivate.jpg", headers=self.auth_headers())
        self.assertIn(response.status_code, {404, 308})


if __name__ == "__main__":
    unittest.main()
