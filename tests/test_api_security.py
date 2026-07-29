"""
Security tests for FastAPI endpoints in Błyskawica.
Checks token authentication, path boundaries, restricted folders, and CORS configuration.
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blyskawica_app.backend.main import app, STARTUP_TOKEN


class TestAPISecurity(unittest.TestCase):
    """Test API token security and path boundary validations"""

    def setUp(self):
        self.client = TestClient(app)

    def test_get_token(self):
        """Test that the auth token endpoint returns the correct token"""
        response = self.client.get(
            "/api/auth/token",
            headers={"X-Internal-Request": "sparkle-tauri-shell"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data["token"], STARTUP_TOKEN)

    def test_permission_level_unauthorized(self):
        """Test that setting permission level without a valid token fails"""
        # No token header
        response = self.client.post("/api/permission_level?level=3")
        self.assertEqual(response.status_code, 401)

        # Invalid token header
        response = self.client.post(
            "/api/permission_level?level=3",
            headers={"X-Blyskawica-Token": "invalid_token_123"}
        )
        self.assertEqual(response.status_code, 401)

    def test_permission_level_authorized(self):
        """Test that setting permission level with a valid token succeeds"""
        # Save original permission level
        status_res = self.client.get("/api/permission_level")
        original_level = status_res.json()["permission_level"]

        try:
            # Set to level 1
            response = self.client.post(
                "/api/permission_level?level=1",
                headers={"X-Blyskawica-Token": STARTUP_TOKEN}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["permission_level"], 1)

            # Set to level 2
            response = self.client.post(
                "/api/permission_level?level=2",
                headers={"X-Blyskawica-Token": STARTUP_TOKEN}
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["permission_level"], 2)
        finally:
            # Restore original permission level
            self.client.post(
                f"/api/permission_level?level={original_level}",
                headers={"X-Blyskawica-Token": STARTUP_TOKEN}
            )

    def test_vibe_code_unauthorized(self):
        """Test that executing code writes without a token is blocked"""
        response = self.client.post(
            "/api/ide/vibe_code",
            data={"path": "test.txt", "content": "hello"}
        )
        self.assertEqual(response.status_code, 401)

    def test_vibe_code_restricted_paths_at_level_2(self):
        """Test that path writes outside workspace at permission level 2 are blocked"""
        # Set level to 2
        self.client.post(
            "/api/permission_level?level=2",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN}
        )

        # Attempt directory traversal / absolute path outside project root
        response = self.client.post(
            "/api/ide/vibe_code",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN},
            data={"path": "../outside_project.txt", "content": "malicious"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Workspace", response.json()["message"])

    def test_vibe_code_system_paths_at_level_3(self):
        """Test that writes to Windows system directories are blocked even at Level 3"""
        # Elevate to Level 3
        self.client.post(
            "/api/permission_level?level=3",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN}
        )

        try:
            # Target a sensitive Windows directory
            system_paths = [
                "C:/Windows/System32/hacked.dll",
                "c:/program files/malicious.exe",
                "c:\\windows\\temp\\malware.exe",
            ]

            for path in system_paths:
                response = self.client.post(
                    "/api/ide/vibe_code",
                    headers={"X-Blyskawica-Token": STARTUP_TOKEN},
                    data={"path": path, "content": "malicious content"}
                )
                self.assertEqual(response.status_code, 403)
                self.assertIn("katalogu systemowym", response.json()["message"])
        finally:
            # Restore to Level 2
            self.client.post(
                "/api/permission_level?level=2",
                headers={"X-Blyskawica-Token": STARTUP_TOKEN}
            )

    def test_execute_system_action_unauthorized(self):
        """Test that system actions cannot be triggered without auth token"""
        response = self.client.post(
            "/api/execute_system_action",
            data={"action": "create_folder", "args": '{"path": "C:/Projekty/test_folder"}'}
        )
        self.assertEqual(response.status_code, 401)

    def test_execute_system_action_forbidden_level_2(self):
        """Test that system actions are forbidden when permission level is less than 3"""
        # Ensure level is 2
        self.client.post(
            "/api/permission_level?level=2",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN}
        )

        response = self.client.post(
            "/api/execute_system_action",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN},
            data={"action": "create_folder", "args": '{"path": "C:/Projekty/test_folder"}'}
        )
        self.assertEqual(response.status_code, 403)

    def test_strict_quarantine_block(self):
        """Test that system actions and code writes are blocked when quarantine is active"""
        # Elevate to Level 3
        self.client.post(
            "/api/permission_level?level=3",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN}
        )
        
        # Modifying core file via vibe_code triggers quarantine
        self.client.post(
            "/api/ide/vibe_code",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN},
            data={"path": "welcome_v9.py", "content": "malicious content"}
        )
        
        # Verify quarantine is active
        status_res = self.client.get("/api/permission_level")
        self.assertTrue(status_res.json()["quarantine_active"])
        
        # Attempt standard file write to safe path - should be blocked due to quarantine!
        response = self.client.post(
            "/api/ide/vibe_code",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN},
            data={"path": "safe_file.txt", "content": "safe content"}
        )
        self.assertEqual(response.status_code, 403)

        # Attempt system action - should be blocked due to quarantine!
        response = self.client.post(
            "/api/execute_system_action",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN},
            data={"action": "create_folder", "args": '{"path": "C:/Projekty/test_folder"}'}
        )
        self.assertEqual(response.status_code, 403)
        
        # Reset quarantine by resetting permission level
        self.client.post(
            "/api/permission_level?level=2",
            headers={"X-Blyskawica-Token": STARTUP_TOKEN}
        )
        status_res = self.client.get("/api/permission_level")
        self.assertFalse(status_res.json()["quarantine_active"])

    def test_cors_origins(self):
        """Test that CORS policy restricts unauthorized origins"""
        # Authorized origin
        res = self.client.options(
            "/api/auth/token",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertEqual(res.headers.get("access-control-allow-origin"), "http://localhost:8000")

        # Unauthorized origin
        res_bad = self.client.options(
            "/api/auth/token",
            headers={
                "Origin": "http://malicious.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertNotEqual(res_bad.headers.get("access-control-allow-origin"), "http://malicious.com")


if __name__ == "__main__":
    unittest.main()
