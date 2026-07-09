"""Tests for the REST API."""

import pytest
from fastapi.testclient import TestClient

from nethical_recon.api import create_app
from nethical_recon.api.config import APIConfig
from nethical_recon.core.models import Target, TargetScope, TargetType
from nethical_recon.core.storage import init_database


@pytest.fixture
def api_config():
    """Create API configuration for testing."""
    return APIConfig(
        secret_key="test_secret_key",
        access_token_expire_minutes=30,
    )


@pytest.fixture
def client(api_config):
    """Create FastAPI test client."""
    app = create_app(api_config)
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Get authentication headers with admin token."""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_key_headers():
    """Get authentication headers with API key."""
    return {"Authorization": "Bearer nethical_test_key_12345"}


class TestHealth:
    """Test health and version endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "database" in data
        assert "worker" in data

    def test_version(self, client):
        """Test version endpoint."""
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "api_prefix" in data


class TestAuthentication:
    """Test authentication endpoints."""

    def test_login_success(self, client):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert "read" in data["scopes"]
        assert "write" in data["scopes"]
        assert "admin" in data["scopes"]

    def test_api_key_authentication(self, client, api_key_headers):
        """Test authentication with API key."""
        response = client.get("/api/v1/auth/me", headers=api_key_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "Test API Key"

    def test_create_api_key(self, client, auth_headers):
        """Test creating a new API key (admin only)."""
        response = client.post(
            "/api/v1/auth/api-keys",
            headers=auth_headers,
            json={"name": "New Test Key", "scopes": ["read"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Test Key"
        assert data["scopes"] == ["read"]
        assert "key" in data
        assert data["key"].startswith("nethical_")


class TestTargets:
    """Test target management endpoints."""

    def test_create_target(self, client, auth_headers):
        """Test creating a target."""
        import uuid

        # Use a unique value to avoid conflicts
        unique_value = f"test-{uuid.uuid4()}.example.com"
        response = client.post(
            "/api/v1/targets",
            headers=auth_headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
                "description": "Test target",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == unique_value
        assert data["type"] == "domain"
        assert "id" in data

    def test_list_targets(self, client, auth_headers):
        """Test listing targets."""
        import uuid

        # Create a target first
        unique_value = f"list-test-{uuid.uuid4()}.example.com"
        client.post(
            "/api/v1/targets",
            headers=auth_headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
            },
        )

        # List targets
        response = client.get("/api/v1/targets", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["page"] == 1

    def test_get_target(self, client, auth_headers):
        """Test getting a specific target."""
        import uuid

        # Create a target
        unique_value = f"get-test-{uuid.uuid4()}.example.com"
        create_response = client.post(
            "/api/v1/targets",
            headers=auth_headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
            },
        )
        target_id = create_response.json()["id"]

        # Get the target
        response = client.get(f"/api/v1/targets/{target_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == target_id
        assert data["value"] == unique_value

    def test_update_target(self, client, auth_headers):
        """Test updating a target."""
        import uuid

        # Create a target
        unique_value = f"update-test-{uuid.uuid4()}.example.com"
        create_response = client.post(
            "/api/v1/targets",
            headers=auth_headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
            },
        )
        target_id = create_response.json()["id"]

        # Update the target
        response = client.patch(
            f"/api/v1/targets/{target_id}",
            headers=auth_headers,
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication."""
        response = client.get("/api/v1/targets")
        assert response.status_code == 401


class TestJobs:
    """Test job management endpoints."""

    def test_create_job_requires_target(self, client, auth_headers):
        """Test creating a job requires a valid target."""
        from uuid import uuid4

        # Try to create a job with non-existent target
        response = client.post(
            "/api/v1/jobs",
            headers=auth_headers,
            json={
                "target_id": str(uuid4()),
                "name": "Test Job",
                "tools": ["nmap"],
            },
        )
        # This should fail at the database level
        assert response.status_code in [404, 500]

    def test_list_jobs(self, client, auth_headers):
        """Test listing jobs."""
        response = client.get("/api/v1/jobs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_jobs_with_filters(self, client, auth_headers):
        """Test listing jobs with filters."""
        response = client.get(
            "/api/v1/jobs?status=completed&page=1&page_size=10",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


class TestFindings:
    """Test finding endpoints."""

    def test_list_findings(self, client, auth_headers):
        """Test listing findings."""
        response = client.get("/api/v1/findings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_findings_with_severity_filter(self, client, auth_headers):
        """Test listing findings with severity filter."""
        response = client.get(
            "/api/v1/findings?severity=high",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_findings_with_pagination(self, client, auth_headers):
        """Test listing findings with pagination."""
        response = client.get(
            "/api/v1/findings?page=1&page_size=20",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20


class TestRuns:
    """Test tool run endpoints."""

    def test_list_runs(self, client, auth_headers):
        """Test listing tool runs."""
        response = client.get("/api/v1/runs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data


class TestReports:
    """Test report endpoints."""

    def test_get_report_for_nonexistent_job(self, client, auth_headers):
        """Test getting report for non-existent job."""
        from uuid import uuid4

        response = client.get(
            f"/api/v1/reports/{uuid4()}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestAuthorization:
    """Test authorization and scopes."""

    def test_viewer_cannot_create_target(self, client):
        """Test that viewer role cannot create targets."""
        # Login as viewer
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "viewer", "password": "admin123"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to create a target
        response = client.post(
            "/api/v1/targets",
            headers=headers,
            json={
                "value": "viewer-test.com",
                "type": "domain",
                "scope": "in_scope",
            },
        )
        assert response.status_code == 403

    def test_viewer_can_read(self, client):
        """Test that viewer role can read."""
        # Login as viewer
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "viewer", "password": "admin123"},
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Read targets
        response = client.get("/api/v1/targets", headers=headers)
        assert response.status_code == 200

    def test_operator_can_write(self, client, auth_headers):
        """Test that operator role can write."""
        import uuid

        # Login as operator
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "operator", "password": "admin123"},
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a target
        unique_value = f"operator-test-{uuid.uuid4()}.com"
        response = client.post(
            "/api/v1/targets",
            headers=headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
            },
        )
        assert response.status_code == 201

    def test_only_admin_can_delete(self, client):
        """Test that only admin can delete targets."""
        import uuid

        # Login as admin and create a target
        admin_response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"},
        )
        admin_token = admin_response.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        unique_value = f"delete-test-{uuid.uuid4()}.com"
        create_response = client.post(
            "/api/v1/targets",
            headers=admin_headers,
            json={
                "value": unique_value,
                "type": "domain",
                "scope": "in_scope",
            },
        )
        target_id = create_response.json()["id"]

        # Try to delete as operator
        operator_response = client.post(
            "/api/v1/auth/token",
            data={"username": "operator", "password": "admin123"},
        )
        operator_token = operator_response.json()["access_token"]
        operator_headers = {"Authorization": f"Bearer {operator_token}"}

        response = client.delete(f"/api/v1/targets/{target_id}", headers=operator_headers)
        assert response.status_code == 403

        # Delete as admin should work
        response = client.delete(f"/api/v1/targets/{target_id}", headers=admin_headers)
        assert response.status_code == 204


class TestOpenAPI:
    """Test OpenAPI documentation."""

    def test_openapi_json(self, client):
        """Test that OpenAPI JSON is available."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_swagger_ui(self, client):
        """Test that Swagger UI is available."""
        response = client.get("/api/v1/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test that ReDoc is available."""
        response = client.get("/api/v1/redoc")
        assert response.status_code == 200
