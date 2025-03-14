import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Sample test user credentials
test_user = {
    "username": "testuser",
    "password": "testpassword"
}

# Store JWT token for authentication tests
jwt_token = None

# Test User Registration
def test_register_user():
    response = client.post("/register", json=test_user)
    assert response.status_code == 201 or response.status_code == 400  # 400 if user already exists

# Test User Login
def test_login_user():
    global jwt_token
    response = client.post("/login", json=test_user)
    assert response.status_code == 200
    jwt_token = response.json().get("access_token")
    assert jwt_token is not None

# Helper function to set authorization header
def get_auth_headers():
    return {"Authorization": f"Bearer {jwt_token}"}

# Test Fetch Users (Requires Authentication)
def test_get_users():
    response = client.get("/users", headers=get_auth_headers())
    assert response.status_code == 200

# Test Event Creation (Requires Authentication)
def test_create_event():
    event_data = {
        "title": "Tech Conference",
        "description": "A conference about technology trends",
        "date": "2025-05-20",
        "location": "Online"
    }
    response = client.post("/events", json=event_data, headers=get_auth_headers())
    assert response.status_code == 201
    assert response.json()["title"] == "Tech Conference"

# Test Fetching Events
def test_get_events():
    response = client.get("/events")
    assert response.status_code == 200

# Test Joining an Event (Assume Event ID 1 Exists)
def test_join_event():
    response = client.post("/events/1/join", headers=get_auth_headers())
    assert response.status_code in [200, 404]  # 404 if event does not exist

# Test Leaving an Event
def test_leave_event():
    response = client.delete("/events/1/leave", headers=get_auth_headers())
    assert response.status_code in [200, 404]

# Test Unauthorized Access (No Token)
def test_unauthorized_access():
    response = client.get("/users")
    assert response.status_code == 401  # Should return unauthorized error

if __name__ == "__main__":
    pytest.main()
