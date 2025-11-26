"""
Test suite for Mergington High School API

Tests cover:
- Getting all activities
- Signing up for activities
- Unregistering from activities
- Error handling for invalid activities and duplicate signups
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_all_activities(self):
        """Test that get_activities returns all available activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all expected activities are present
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Soccer Team", "Basketball Club", "Art Workshop",
            "Drama Club", "Mathletes", "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data
            
    def test_get_activities_returns_activity_details(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_for_activity_success(self):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@student.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@student.edu" in data["message"]
        
    def test_signup_for_activity_invalid_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Non-Existent Activity/signup",
            params={"email": "test@student.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@student.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Basketball Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Basketball Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_from_activity_success(self):
        """Test successfully unregistering from an activity"""
        email = "unregister@student.edu"
        
        # Sign up first
        client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Soccer Team/participants",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_from_invalid_activity(self):
        """Test unregistering from non-existent activity"""
        response = client.delete(
            "/activities/Non-Existent Activity/participants",
            params={"email": "test@student.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregistering when not signed up"""
        response = client.delete(
            "/activities/Art Workshop/participants",
            params={"email": "notsignedup@student.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]


class TestRootRedirect:
    """Tests for root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
