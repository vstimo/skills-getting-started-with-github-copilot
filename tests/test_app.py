import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestActivitiesAPI:
    """Test suite for Mergington High School Activities API"""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """Test GET /activities returns all activities with correct structure"""
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # All activities from the app

        # Check structure of first activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_has_expected_participants(self, client: TestClient):
        """Test GET /activities returns activities with correct participant data"""
        response = client.get("/activities")
        assert response.status_code == 200

        data = response.json()
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 2

    def test_get_root_redirects_to_static_index(self, client: TestClient):
        """Test GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"

    def test_signup_success(self, client: TestClient):
        """Test successful signup for an activity"""
        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])

        # Sign up new participant
        response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
        assert response.status_code == 200

        data = response.json()
        assert "Signed up test@example.com for Chess Club" in data["message"]

        # Verify participant was added
        response = client.get("/activities")
        updated_data = response.json()
        assert len(updated_data["Chess Club"]["participants"]) == initial_count + 1
        assert "test@example.com" in updated_data["Chess Club"]["participants"]

    def test_signup_duplicate_email(self, client: TestClient):
        """Test signup fails when email is already signed up"""
        # Try to sign up existing participant again
        response = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
        assert response.status_code == 400

        data = response.json()
        assert "Student is already signed up for this activity" in data["detail"]

    def test_signup_invalid_activity(self, client: TestClient):
        """Test signup fails for non-existent activity"""
        response = client.post("/activities/NonExistent%20Activity/signup?email=test@example.com")
        assert response.status_code == 404

        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_success(self, client: TestClient):
        """Test successful unregistration from an activity"""
        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])

        # Unregister existing participant
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200

        data = response.json()
        assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]

        # Verify participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        assert len(updated_data["Chess Club"]["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in updated_data["Chess Club"]["participants"]

    def test_unregister_not_signed_up(self, client: TestClient):
        """Test unregister fails when email is not signed up"""
        response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
        assert response.status_code == 400

        data = response.json()
        assert "Student is not signed up for this activity" in data["detail"]

    def test_unregister_invalid_activity(self, client: TestClient):
        """Test unregister fails for non-existent activity"""
        response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@example.com")
        assert response.status_code == 404

        data = response.json()
        assert "Activity not found" in data["detail"]