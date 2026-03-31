import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities


# Module-level fixture to reset activities before each test
@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_state = {
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
        "Basketball Team": {
            "description": "Compete in interscholastic basketball tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }

    activities.clear()
    activities.update(copy.deepcopy(initial_state))

    yield

    activities.clear()
    activities.update(copy.deepcopy(initial_state))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activity_count = 9

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint"""

    def test_signup_happy_path(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participant_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_participant_count + 1

    def test_signup_duplicate_raises_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_participant_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up"
        assert len(activities[activity_name]["participants"]) == initial_participant_count

    def test_signup_unknown_activity_raises_404(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint"""

    def test_delete_participant_happy_path(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_participant_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_participant_count - 1

    def test_delete_missing_participant_raises_404(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "notamember@mergington.edu"
        initial_participant_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"
        assert len(activities[activity_name]["participants"]) == initial_participant_count

    def test_delete_unknown_activity_raises_404(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
