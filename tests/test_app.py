"""
Tests for the Mergington High School Activities API
Using AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team for practice and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ethan@mergington.edu", "maria@mergington.edu"]
        },
        "Swim Club": {
            "description": "Swim training and aquatic fitness sessions",
            "schedule": "Mondays, Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "nina@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, improv, and stage production skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "liam@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "jacob@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["elena@mergington.edu", "mason@mergington.edu"]
        }
    }
    
    activities.clear()
    activities.update(original_activities)
    yield
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        # Arrange
        expected_count = 9
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(activities) == expected_count
        for activity in expected_activities:
            assert activity in activities
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activity details are properly formatted"""
        # Arrange
        activity_name = "Chess Club"
        expected_description = "Learn strategies and compete in chess tournaments"
        expected_schedule = "Fridays, 3:30 PM - 5:00 PM"
        expected_max_participants = 12
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        chess_club = activities[activity_name]
        
        # Assert
        assert chess_club["description"] == expected_description
        assert chess_club["schedule"] == expected_schedule
        assert chess_club["max_participants"] == expected_max_participants
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_includes_current_participants(self, client):
        """Test that participant list is included in response"""
        # Arrange
        activity_name = "Chess Club"
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_count = 2
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        actual_participants = activities[activity_name]["participants"]
        
        # Assert
        assert len(actual_participants) == expected_count
        for participant in expected_participants:
            assert participant in actual_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_adds_participant(self, client):
        """Test that signup adds a new participant"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={new_email}"
        )
        result = response.json()
        
        # Verify participant was added
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in result
        assert new_email in result["message"]
        assert new_email in updated_activities[activity]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up a participant twice fails"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act - First signup
        client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={new_email}"
        )
        
        # Act - Second signup (duplicate)
        duplicate_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={new_email}"
        )
        duplicate_result = duplicate_response.json()
        
        # Assert
        assert duplicate_response.status_code == 400
        assert "already signed up" in duplicate_result["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup to non-existent activity fails"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity.replace(' ', '%20')}/signup?email={email}"
        )
        result = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]
    
    def test_signup_to_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        # Arrange
        student_email = "multiactivity@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class"]
        
        # Act
        responses = []
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={student_email}"
            )
            responses.append(response)
        
        # Verify both signups
        activities_response = client.get("/activities")
        updated_activities = activities_response.json()
        
        # Assert
        for response in responses:
            assert response.status_code == 200
        
        for activity in activities_to_join:
            assert student_email in updated_activities[activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister removes a participant"""
        # Arrange
        activity = "Chess Club"
        student_email = "michael@mergington.edu"
        
        # Verify initial state
        activities_response = client.get("/activities")
        activities = activities_response.json()
        initial_count = len(activities[activity]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={student_email}"
        )
        result = response.json()
        
        # Get updated state
        updated_activities_response = client.get("/activities")
        updated_activities = updated_activities_response.json()
        updated_count = len(updated_activities[activity]["participants"])
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in result["message"]
        assert student_email not in updated_activities[activity]["participants"]
        assert updated_count == initial_count - 1
    
    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-enrolled student fails"""
        # Arrange
        activity = "Chess Club"
        nonexistent_email = "notstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={nonexistent_email}"
        )
        result = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in result["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from non-existent activity fails"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity.replace(' ', '%20')}/unregister?email={email}"
        )
        result = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete signup and unregister workflow"""
        # Arrange
        activity = "Programming Class"
        student_email = "workflow@mergington.edu"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_activities = initial_response.json()
        initial_count = len(initial_activities[activity]["participants"])
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={student_email}"
        )
        
        # Verify signup occurred
        after_signup_response = client.get("/activities")
        after_signup_activities = after_signup_response.json()
        after_signup_count = len(after_signup_activities[activity]["participants"])
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={student_email}"
        )
        
        # Get final state
        final_response = client.get("/activities")
        final_activities = final_response.json()
        final_count = len(final_activities[activity]["participants"])
        
        # Assert
        assert signup_response.status_code == 200
        assert student_email in after_signup_activities[activity]["participants"]
        assert after_signup_count == initial_count + 1
        
        assert unregister_response.status_code == 200
        assert student_email not in final_activities[activity]["participants"]
        assert final_count == initial_count


class TestRootEndpoint:
    """Tests for root endpoint redirection"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to static/index.html"""
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location
