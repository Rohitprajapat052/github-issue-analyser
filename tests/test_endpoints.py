"""Basic tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check passed")


def test_scan_invalid_format():
    """Test scan with invalid repo format"""
    response = client.post(
        "/scan",
        json={"repo": "invalid-format"}
    )
    assert response.status_code == 400
    assert "Invalid repository format" in response.json()["detail"]["error"]
    print("✅ Invalid format validation passed")


def test_analyze_before_scan():
    """Test analyze endpoint before scanning repo"""
    response = client.post(
        "/analyze",
        json={
            "repo": "nonexistent/repo",
            "prompt": "Test prompt"
        }
    )
    assert response.status_code == 400
    assert "not yet scanned" in response.json()["detail"]["error"]
    print("✅ Analyze before scan validation passed")


def test_scan_nonexistent_repo():
    """Test scan with non-existent repository"""
    response = client.post(
        "/scan",
        json={"repo": "thisdoesnotexist12345/fakerepo99999"}
    )
    assert response.status_code == 404
    print("✅ Non-existent repo handling passed")


def test_analyze_empty_prompt():
    """Test analyze with empty prompt"""
    response = client.post(
        "/analyze",
        json={
            "repo": "microsoft/vscode",
            "prompt": ""
        }
    )
    assert response.status_code == 400
    assert "Empty prompt" in response.json()["detail"]["error"]
    print("✅ Empty prompt validation passed")


if __name__ == "__main__":
    print("🧪 Running tests...\n")
    test_root_endpoint()
    test_scan_invalid_format()
    test_analyze_before_scan()
    test_scan_nonexistent_repo()
    test_analyze_empty_prompt()
    print("\n🎉 All tests passed!")